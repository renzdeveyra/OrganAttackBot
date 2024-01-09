import discord
from discord.ext import commands
from discord import app_commands

import Game.game as game
from Game.utils import display_organs, generate_attack_embeds, PlayCard, Menu

class GameInitializationCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.players_list = {}
        self.games_registry = {}
        self.game_key = ''

    @app_commands.command(name='join', description='Join a game.')
    async def join(self, interaction: discord.Interaction):
        user_mention = interaction.user.mention
        user_name = interaction.user.name
        # if user_name in players_list:
        #     print("this")
        #     await interaction.response.send_message(f"Last time I checked, you already joined {user_name}...")
        #     return
        # elif user in games_registry[game_key_ref]['players']:
        #     await interaction.response.send_message(f"U okay, {user}?\nYou're literally playing right now (◕︿◕✿)")
        #     return
        if len(self.players_list.keys()) == 6:
            await interaction.response.send_message(f"There's already 6 of you! (,,>﹏<,,)\n"
                                                    f'Type `/players` to see for yourself (¬_¬")')
            return
        else:
            self.players_list[user_name] = user_mention
            print(f"Added {user_name} as {user_mention}")
            await interaction.response.send_message(f"Hello, {user_mention}\n"
                                                    "You have joined the game! (✿◠‿◠)")

    @app_commands.command(name='players-list', description='View the players in your lobby.')
    async def players(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Hello, {interaction.user.mention}\n These are the players\n"
            f"(☞ ͡° ͜ʖ ͡°)☞  {', '.join(self.players_list.keys())}"
        )

    @app_commands.command(name='start', description="Let's play!")
    async def start(self, interaction: discord.Interaction):
        user = interaction.user.mention
        # if user in games_registry[game_key_ref]['players']:
        #     await interaction.response.send_message(f"U okay, {user}?\nYou're literally playing right now (◕︿◕✿)")
        if len(self.players_list) < 2:
            await interaction.response.send_message("fr? (ಥ ͜ʖಥ)")
        else:
            Game = game.Game(self.players_list)
            self.game_key = f"{user}'s_game_{len(self.games_registry) + 1}"
            print(f"Game key: {self.game_key}")
            self.games_registry[self.game_key] = {'game': Game, 'players': self.players_list, 'started': True}
            Game.start()
            self.players_list.clear()
            organs_distribution = display_organs(Game.hands['organ'])

            await interaction.response.send_message(
                f"🩷 **Game Start!!** 🩷\n\nGood luck! (づ｡◕‿‿◕｡)づ\n\n {organs_distribution}\r"
                "Here are your **Organs**!\nTake good care of them! (◡‿◡✿)"
            )
            print(f"Turn order: {Game.turn}")

    @app_commands.command(name='attack', description='View your Hand hidden from other players and play them!')
    async def attack(self, interaction: discord.Interaction):
        user = interaction.user.mention
        Game = self.games_registry[self.game_key]['game']
        embeds = generate_attack_embeds(Game, user)
        cards_select = PlayCard(self.games_registry, self.game_key)

        view = Menu()

        if Game.turn[0] == user:
            for i in range(Game.attack_hand_count):
                card = Game.hands['attack'][user].cards[i].name
                card_type = Game.hands['attack'][user].cards[i].card_type.value
                cards_select.options.append(
                    # discord.SelectOption(label=Game.attack_assignments[user].get_card(i).name,
                    #                      description=Game.attack_assignments[user].get_card(i).card_type)
                    discord.SelectOption(label=card,
                                         description=card_type)
                )

            view = Menu.add_item(Menu(), cards_select)
        await interaction.response.send_message(view=view, embeds=embeds, ephemeral=True)

async def setup(client: commands.Bot):
    await client.add_cog(GameInitializationCog(client))
