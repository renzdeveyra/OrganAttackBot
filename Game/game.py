from collections import deque
from enum import Enum, auto
import random
from collections import namedtuple

# canonical card types
class CardType(Enum):
    """
    Enum representing the types of cards in the game.

    Attributes:
        ORGAN: Represents an organ card.
        ORGAN_WILD: Represents a wild organ card.
        AFFLICTION: Represents an affliction card.
        WILD: Represents a wild card.
        NECROSIS: Represents a necrosis card.
        METASTATIS: Represents a metastatis card.
        TACTICAL: Represents a tactical card.
        INSTANT: Represents an instant card.
        RESISTANCE: Represents a resistance card.
        CURE: Represents a cure card.
        POISON: Represents a poison card.
        BUREAUCRACY: Represents a bureaucracy card.
    """
    ORGAN = 'Organ'
    ORGAN_WILD = 'Organ Wild'
    AFFLICTION = 'Affliction'
    WILD = 'Wild'
    NECROSIS = 'Necrosis'
    METASTATIS = 'Metastasis'
    TACTICAL = 'Tactical'
    INSTANT = 'Instant'
    RESISTANCE = 'Resistance'
    CURE = 'Cure'
    POISON = 'Poison'
    BUREAUCRACY = 'Bureaucracy'

organ_distribution = {2: 12, 3: 8, 4: 6, 5: 4, 6: 4, 7: 3, 8: 3}

class GameState(Enum):
    START = auto()
    PLAY = auto()
    END = auto()

class Game:
    def __init__(self, players: dict[str, str]):
        self.players = list(players.values())
        self.players_mentions = list(players.keys())
        self.organ_deck = Deck(list(organs))
        self.organ_deck.shuffle()
        self.attack_deck = Deck(list(attacks))
        self.attack_deck.shuffle()
        self.hands = {'organ': {}, 'attack': {}}
        self.turn = deque()
        self.turn_stack = []  # a list of all action strings for players to refer to
        self.rotations = 0
        self.current_player = self.turn[0] if len(self.turn) > 0 else None
        self.SitusInversus = False
        self.ongoing_effects = {}
        self.organ_hand_count = organ_distribution[len(players)]
        self.attack_hand_count = 5
        self.state = GameState.START

    def start(self):
        print(f"Starting game with {self.players}")
        first_player_mark = self.organ_deck.get_cards_by_type(CardType.ORGAN_WILD)

        self.assign_initial_hands()

        for user, organ_hand in self.hands['organ'].items():
            if organ_hand and first_player_mark in organ_hand:
                self.set_turn_order(user)
        self.state = GameState.PLAY

    def assign_initial_hands(self):
        for player in self.players:
            self.hands['organ'][player] = Hand(self.organ_deck.draw(self.organ_hand_count))
            self.hands['attack'][player] = Hand(self.attack_deck.draw(self.attack_hand_count))

    def set_turn_order(self, first_player: str):
        self.players = list(self.players)
        print(f"Preserved copy of players: {self.players}")
        self.turn.append(first_player)
        remaining_players = [player for player in self.players if player != first_player]
        random.shuffle(remaining_players)
        self.turn.extend(remaining_players)

    def handle_effect_duration(self):
        for effect, details in self.ongoing_effects.items():
            details['duration'] -= 1
            if details['duration'] == 0:
                del self.ongoing_effects[effect]

    def handle_turn(self):
        if self.state != GameState.PLAY:
            raise Exception('Invalid game state')
        action = 'action string generated from user actions within his turn'
        self.turn_stack.append(action)
        print(f"Pre-handled turn: {self.turn}")
        self.rotate_clockwise() if not self.SitusInversus else self.rotate_counterclockwise()
        self.rotations += 1
        print(f"Post-handled turn: {self.turn}")
        self.state = GameState.END

    def rotate_counterclockwise(self):
        self.turn.rotate(-1)

    def rotate_clockwise(self):
        self.turn.rotate(1)

class Card:
    def __init__(self, name: str, card_type: CardType):
        self.name = name
        self.card_type = card_type

    def __str__(self):
        return self.name

class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    def __str__(self):
        return '\n'.join([str(card) for card in self.cards])

    def __len__(self):
        return len(self.cards)

    def __contains__(self, card):
        return card in self.cards

    def get_card_by_name(self, name: str):
        return next(card for card in self.cards if card.name == name)

    def get_cards_by_type(self, card_type: CardType):
        result = [card for card in self.cards if card.card_type == card_type]
        if len(result) == 0:
            raise Exception(f'No cards of type {card_type} found.')
        return result

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1):
        if len(self.cards) < count:
            raise Exception('Not enough cards in the deck.')
        drawn_cards = [self.cards.pop() for _ in range(count)]
        return drawn_cards

    def add_cards(self, cards):
        if not isinstance(cards, list):
            cards = [cards]
        self.cards.extend(cards)

    def remove_cards(self, cards_to_remove):
        if len(cards_to_remove) > 1:
            for card in cards_to_remove:
                self.cards.remove(card)
        elif len(cards_to_remove) == 1:
            self.cards.remove(cards_to_remove.pop())
        else:
            raise Exception('No cards to remove.')

class Hand:
    def __init__(self, cards: list[Card]):
        self.cards = deque(cards)

    def add_card(self, card: Card):
        self.cards.append(card)

    def draw(self, count=1):  # for 'Common Cold'
        if len(self.cards) < count:
            raise Exception('Not enough cards in hand.')
        drawn_cards = random.sample(self.cards, count)
        self.cards = deque([card for card in self.cards if card not in drawn_cards])
        return drawn_cards

    def get_card(self, card_name: str):
        for card in self.cards:
            if card.name == card_name:
                return card
        raise Exception('Card not found in hand.')

    def has_card(self, card: Card) -> bool:
        return card in self.cards

class Organ(Card):
    def __init__(self, name, card_type, health: int, description: str):
        super().__init__(name, card_type)
        self.max_health = health  # will function as a reference
        self.health = health  # values will be manipulated
        self.description = description

    def __str__(self):
        return f'{self.health} ❤️     {self.name}\n'

    def revive(self):
        self.health = 2

    def damage(self):
        if self.health != 0:
            self.health -= 1
        else:
            raise Exception('Organ is already dead.')

    def heal(self):
        if self.health == 0:
            raise Exception('Organ is already dead.')
        if self.health != self.max_health:
            self.health += 1
        else:
            raise Exception('Organ is already healthy.')

    def kill(self):
        self.health = 0

class OrganNotAffectedException(ValueError):
    """
    Exception raised when an organ is not affected by an affliction.
    """

    def __init__(self, message="The organ is not affected by this Affliction."):
        super().__init__(message)

    def get_message(self):
        return self.args[0]

    def __str__(self):
        return "The organ is not affected by this Affliction."


class Damage(Card):
    def __init__(self, name: str, card_type: CardType, attacks_organs: list[Organ], removes_organ: Organ = None):
        super().__init__(name, card_type)
        self.attacks_organs = organs if Organ_Wild in attacks_organs else list(attacks_organs)
        self.removes_organ = organs if Organ_Wild == removes_organ else [removes_organ]
        # this organ will receive fatal damage

    def attack(self, organ: Organ):
        if organ in self.removes_organ:
            organ.damage()
            organ.damage()
        elif organ in self.attacks_organs:
            organ.damage()
        else:
            raise OrganNotAffectedException(f'The {organ} is not affected by this Affliction.')

class DiscardPile:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    def add_cards(self, cards):
        self.cards.extend(cards)

    def remove_cards(self, cards_to_remove):
        if len(cards_to_remove) > 1:
            return [self.cards.remove(card) for card in cards_to_remove]
        elif len(cards_to_remove) == 1:
            return self.cards.remove(cards_to_remove.pop())
        else:
            raise Exception('No cards to remove.')

# Organ Cards
Spleen = Organ('Spleen', CardType.ORGAN, 2, "This silent protector filters out old blood and produces white blood "
                                            "cells for the immune system.")
Heart = Organ('Heart', CardType.ORGAN, 2, "AKA the cardiac muscle, the heart pumps blood to the rest of the body, "
                                          "delivering much needed oxygen and nutrients.")
Lungs = Organ('Lungs', CardType.ORGAN, 2, "Connected by the bronchi that branch from the trachea, the lungs breathe "
                                          "air and put oxygen to good use.")
Brain = Organ('Brain', CardType.ORGAN, 2, "The brain consists of multiple lobes that work independently as well as "
                                          "together to control everything from movement and reflexes to thoughts, "
                                          "memories, language, and emotion. Use it wisely.")
Liver = Organ('Liver', CardType.ORGAN, 2, "The liver helps filter blood, aids in digestion by breaking down fats and "
                                          "proteins and producing bile, and stores glycogen (a type of sugar) to use "
                                          "as energy")
Kidneys = Organ('Kidneys', CardType.ORGAN, 2, "Located on either side of your back, kidneys prepare waste for liquid "
                                              "removal via the bladder, assist with the red blood cell pressure, and " 
                                              "produce an active form of Vitamin D. Go team!")
Stomach = Organ('Stomach', CardType.ORGAN, 2, "At the end of the esophagus, this acid-producing bag starts to further "
                                              "break down those bites that you clearly didn't chew enough.")
Bowels = Organ('Bowels', CardType.ORGAN, 2, "Consisting of the large intestine (colon) and small intestine, the bowels "
                                            "finalize the digestion process, ensuring a proper poo.")
Esophagus = Organ('Esophagus', CardType.ORGAN, 2, "The food pipe, it connects the throat to the stomach.")
Skin = Organ('Skin', CardType.ORGAN, 2, "The largest organ in your body is that hairy coat you call your skin. "
                                        "Moisturize it or lose it.")
Eyes = Organ('Eyes', CardType.ORGAN, 2, "Perceiving vision never looked this good. Light passes through the pupil, "
                                        "gets processed by rods and cones into usable info for the brain.")
Bones = Organ('Bones', CardType.ORGAN, 2, "Bones give you that distinct human-like appearance so we can tell each "
                                          "other apart from jellyfish. They also contain marrow, which produces new "
                                          "cells.")
Skeletal_Muscles = Organ('Skeletal Muscles', CardType.ORGAN, 2, "Expand. Contract. Repeat. Your bones go nowhere "
                                                                "without these dudes.")
Bladder = Organ('Bladder', CardType.ORGAN, 2, "The bladder stores urine that's been filtered by the kidneys and "
                                              "attempts to hold it until you're ready to go pee pee.")
Pancreas = Organ('Pancreas', CardType.ORGAN, 2, "The pancreas produces insulin for the body, which regulates how "
                                                "the body breaks down sugars and carbohydrates. Dorp.")
GallBladder = Organ('GallBladder', CardType.ORGAN, 2, "The gallbladder is a little dude that collects and stores "
                                                      "extra bile produced by the liver.")
Appendix = Organ('Appendix', CardType.ORGAN, 2, "A tiny organ attached to the large intestine, its function has been  "
                                                "the subject of debate, but some believe it helps by providing good "
                                                "bacteria to the digestive tract after illness.")
Thyroid = Organ('Thyroid', CardType.ORGAN, 2, "Located in your neck, the thyroid produces hormone that regulates "
                                              "metabolic rate, affecting pretty much every organ. Sometimes that power "
                                              "can go to its head.")
Tonsils = Organ('Tonsils', CardType.ORGAN, 2, "Located in the back of the throat, tonsils trap airborne bacteria and "
                                              " produce immune cells that help kill germs and prevent infections.")
Nose = Organ('Nose', CardType.ORGAN, 2, "That thing on your face that smells.")
Tongue = Organ('Tongue', CardType.ORGAN, 2, "That muscle in your mouth that moves food to the back of your throat, "
                                            "and helps taste pizza.")
Trachea = Organ('Trachea', CardType.ORGAN, 2, "The windpipe, it directs air from the mouth and nose through the "
                                              "bronchi and into the lungs.")
Teeth = Organ('Teeth', CardType.ORGAN, 2, "The human adult mouth has 32 teeth if you include wisdom teeth. It has 4 "
                                          "teeth if you ignore 28 of them")
Organ_Wild = Organ('**OrganWild**', CardType.ORGAN_WILD, 4, "Affected by any AFFLICTION card, but requires 4 "
                                                            "AFFLICTIONS to remove.\n**Can Not be brought back from "
                                                            "the Organ discard pile**")

organs = [Spleen, Heart, Lungs, Brain, Liver, Kidneys, Stomach, Bowels, Esophagus, Skin, Eyes, Bones, Skeletal_Muscles,
          Bladder, Pancreas, GallBladder, Appendix, Thyroid, Tonsils, Nose, Tongue, Trachea, Teeth, Organ_Wild]


# Damage Cards
# Affliction Cards
Diabetes = Damage('Diabetes', CardType.AFFLICTION, [Pancreas])
Mental_Illness = Damage('Mental Illness', CardType.AFFLICTION, [Brain])
Cirrhosis = Damage('Cirrhosis', CardType.AFFLICTION, [Liver])
Enamel_Erosion = Damage('Enamel Erosion', CardType.AFFLICTION, [Teeth])
Nosebleed = Damage('Nosebleed', CardType.AFFLICTION, [Nose])
Fracture = Damage('Fracture', CardType.AFFLICTION, [Bones])
Conjunctivitis = Damage('Conjunctivitis', CardType.AFFLICTION, [Eyes])
URI = Damage('Upper Respiratory Infection', CardType.AFFLICTION, [Trachea, Nose, Lungs], Trachea)
Thyroiditis = Damage('Thyroiditis', CardType.AFFLICTION, [Thyroid])
Foreign_Object_in_Eye = Damage('Foreign Object in Eye', CardType.AFFLICTION, [Eyes])
IBS_d = Damage('Irritable Bowel Syndrome with Diarrhea', CardType.AFFLICTION, [Bowels])
Hot_Coffee = Damage('Hot Coffee', CardType.AFFLICTION, [Tongue])
Love = Damage('Love', CardType.AFFLICTION, [Brain, Heart, Stomach], Brain)
Day_old_Burrito = Damage('Day-old Burrito', CardType.AFFLICTION, [Bowels, Stomach])
Total_Colectomy = Damage('Total Colectomy', CardType.AFFLICTION, [Appendix, Bowels], Appendix)
Pancreatitis = Damage('Pancreatitis', CardType.AFFLICTION, [GallBladder, Pancreas], GallBladder)
Heartburn = Damage('Heartburn', CardType.AFFLICTION, [Esophagus])
Osteoporosis = Damage('Osteoporosis', CardType.AFFLICTION, [Bones])
Walking_Pneumonia = Damage('Walking Pneumonia', CardType.AFFLICTION, [Lungs, Trachea])
Hepatosplenomegaly = Damage('Hepatosplenomegaly', CardType.AFFLICTION, [Spleen, Liver])
Lacerated_Spleen = Damage('Lacerated Spleen', CardType.AFFLICTION, [Spleen])
Muscular_Dystrophy = Damage('Muscular Dystrophy', CardType.AFFLICTION, [Skeletal_Muscles])
Arrhythmia = Damage('Arrhythmia', CardType.AFFLICTION, [Heart])
Ruptured_Appendix = Damage('Ruptured Appendix', CardType.AFFLICTION, [], Appendix)
Appendicitis = Damage('Appendicitis', CardType.AFFLICTION, [Appendix])
Chrons = Damage("Chron's", CardType.AFFLICTION, [Bowels])
Acne = Damage('Acne', CardType.AFFLICTION, [Skin])
Cystic_Fibrosis = Damage('Cystic Fibrosis', CardType.AFFLICTION, [Lungs, Pancreas])
Hypothyroidism = Damage('Hypothyroidism', CardType.AFFLICTION, [Thyroid])
Tonsillitis = Damage('Tonsillitis', CardType.AFFLICTION, [Tonsils])
Asthma = Damage('Asthma', CardType.AFFLICTION, [Lungs, Trachea])
Chronic_Strep_Throat = Damage('Chronic Strep Throat', CardType.AFFLICTION, [Tonsils])
Biliary_Dyskinesia = Damage('Biliary Dyskinesia', CardType.AFFLICTION, [GallBladder])
Calcium_Stones = Damage('Calcium Stones', CardType.AFFLICTION, [Kidneys, Bladder])
Hypersplenism = Damage('Hypersplenism', CardType.AFFLICTION, [Spleen])
Hyperthyroidism = Damage('Hyperthyroidism', CardType.AFFLICTION, [Thyroid])
Congestion = Damage('Congestion', CardType.AFFLICTION, [Nose])
Esophageal_Stricture = Damage('Esophageal Stricture', CardType.AFFLICTION, [Esophagus])
Inflamed_Taste_Bud = Damage('Inflamed Taste Bud', CardType.AFFLICTION, [Tongue])
Stroke = Damage('Stroke', CardType.AFFLICTION, [Brain])
Overactive_Bladder = Damage('Overactive Bladder', CardType.AFFLICTION, [Bladder])
Fatty_Liver = Damage('Fatty Liver', CardType.AFFLICTION, [Liver])
Tendonitis = Damage('Tendonitis', CardType.AFFLICTION, [Skeletal_Muscles, Bones])
Tracheal_Stenosis = Damage('Tracheal Stenosis', CardType.AFFLICTION, [Trachea])
Cavity = Damage('Cavity', CardType.AFFLICTION, [Teeth])
Kidney_Donor = Damage('Kidney Donor', CardType.AFFLICTION, [Kidneys])
UTI = Damage('Urinary Tract Infection', CardType.AFFLICTION, [Bladder, Kidneys])
Muscle_Contusion = Damage('Muscle Contusion', CardType.AFFLICTION, [Skeletal_Muscles, Skin])
Glaucoma = Damage('Glaucoma', CardType.AFFLICTION, [Eyes])
Psoriasis = Damage('Psoriasis', CardType.AFFLICTION, [Skin])
Heart_Attack = Damage('Heart Attack', CardType.AFFLICTION, [Heart])
Stomach_Ulcer = Damage('Stomach Ulcer', CardType.AFFLICTION, [Stomach])
Tonsil_Stones = Damage('Tonsil Stones', CardType.AFFLICTION, [Tonsils])
Gallstones = Damage('Gallstones', CardType.AFFLICTION, [GallBladder])
Vomit = Damage('Vomit', CardType.AFFLICTION, [Stomach, Esophagus, Tongue, Teeth])

# Wild Cards
Malpractice = Damage('Malpractice', CardType.WILD, [Organ_Wild])
Infection = Damage('Infection', CardType.WILD, [Organ_Wild])
Hemorrhage = Damage('Hemorrhage', CardType.WILD, [Organ_Wild])
Benign_Tumor = Damage('Benign Tumor', CardType.WILD, [Organ_Wild])
Cancer = Damage('Cancer', CardType.AFFLICTION, [Organ_Wild])
Hypochondria = Damage('Hypochondria', CardType.WILD, [Organ_Wild])
Botched_Surgery = Damage('Botched Surgery', CardType.WILD, [Organ_Wild])
Multiple_Sclerosis = Damage('Multiple Sclerosis', CardType.WILD, [Organ_Wild])
Neglect = Damage('Neglect', CardType.WILD, [Organ_Wild])

# Necrosis Cards
Necrosis = Damage('Necrosis', CardType.NECROSIS, [], Organ_Wild)

damage_cards = [Diabetes, Mental_Illness, Cirrhosis, Enamel_Erosion, Nosebleed, Fracture, Conjunctivitis, URI,
                Thyroiditis, Foreign_Object_in_Eye, IBS_d, Hot_Coffee, Love, Day_old_Burrito, Total_Colectomy,
                Pancreatitis, Heartburn, Osteoporosis, Walking_Pneumonia, Hepatosplenomegaly, Lacerated_Spleen,
                Muscular_Dystrophy, Arrhythmia, Ruptured_Appendix, Appendicitis, Chrons, Acne, Cystic_Fibrosis,
                Hypothyroidism, Tonsillitis, Asthma, Chronic_Strep_Throat, Biliary_Dyskinesia, Calcium_Stones,
                Hypersplenism, Hyperthyroidism, Congestion, Esophageal_Stricture, Inflamed_Taste_Bud, Stroke,
                Overactive_Bladder, Fatty_Liver, Tendonitis, Tracheal_Stenosis, Cavity, Kidney_Donor, UTI,
                Muscle_Contusion, Glaucoma, Psoriasis, Heart_Attack, Stomach_Ulcer, Tonsil_Stones, Gallstones, Vomit,
                Malpractice, Infection, Hemorrhage, Benign_Tumor, Cancer, Hypochondria, Botched_Surgery,
                Multiple_Sclerosis, Neglect, Necrosis, Necrosis, Necrosis, Necrosis, Necrosis]

attacks = damage_cards

descriptions = {
    CardType.WILD: "Play as an Affliction on any organ.",
    CardType.NECROSIS: "Organ death!\n Remove an opponent's organ.\n(Counts as 2 Afflictions on the Organ Wild Card)",
}
