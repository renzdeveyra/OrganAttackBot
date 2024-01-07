import discord
import game

# Function to generate attack embeds
def generate_attack_embeds(_game: game.Game, user):
    embeds = []
    for i in range(_game.attack_hand_count):
        card = _game.hands['attack'][user].get_card(i)
        title = card.name
        color = embed_color(card.card_type)
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name='Type', value=card.card_type, inline=False)
        if card.card_type == game.CardType.AFFLICTION:
            affliction_details = display_affliction_details(card.attacks_organs, card.removes_organ)
            embed.add_field(name='Attacks', value=', '.join(affliction_details['Attacks']), inline=True)
            embed.add_field(name='Removes', value=affliction_details['Removes'], inline=True)
        else:
            embed.add_field(name='Description', value=game.descriptions[card.card_type], inline=False)
        embeds.append(embed)
    return embeds

def display_organs(organ_assignments: dict[str, game.Hand]):
    return "\n".join([
        f"**{user}'s Organs:**\n{''.join(map(str, organ_hand.cards))}"
        for user, organ_hand in organ_assignments.items()
    ])

# def format_string(text: str):
#     total_length = 60
#     remaining_length = max(total_length - len(text), 0)
#     left_padding = remaining_length // 2
#     right_padding = remaining_length - left_padding
#     formatted_text = '‎ ' * left_padding + text + '‎ ' * right_padding
#     return formatted_text

def display_affliction_details(attacks_organs: list[game.Organ], removes_organ: game.Organ):
    return {
        'Attacks': [organ.name for organ in attacks_organs if organ is not None and organ != removes_organ],
        'Removes': removes_organ.name if removes_organ is not None else 'None'
    }

def embed_color(card_type):
    if card_type == game.CardType.AFFLICTION:
        return discord.Color.red()
    elif card_type == game.CardType.NECROSIS:
        return discord.Color.purple()
    elif card_type == game.CardType.WILD:
        return discord.Color.dark_red()
    else:
        return discord.Color.dark_grey()
