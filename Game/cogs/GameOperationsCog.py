import discord
from discord.ext import commands
from discord import app_commands

import Game.game as game
from Game.utils import generate_attack_embeds, PlayCard, Menu

class GameOperationsCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        # self.GameInitializationCog = self.client.get_cog('GameInitializationCog')

    @app_commands.command(name='attack', description='View your Hand hidden from other players and play them!')
    async def attack(self, interaction: discord.Interaction):
        # games_registry = self.GameInitializationCog.games_registry
        # game_key = self.GameInitializationCog.game_key
        # user = interaction.user.name
        # Game = games_registry[game_key]['game']
        # embeds = generate_attack_embeds(Game, user)
        # cards_select = PlayCard(games_registry, game_key)
        #
        # view = Menu()
        #
        # if Game.turn[0] == user:
        #     for i in range(Game.attack_hand_count):
        #         cards_select.options.append(
        #             discord.SelectOption(label=Game.attack_assignments[user].get_card(i).name,
        #                                  description=Game.attack_assignments[user].get_card(i).card_type)
        #         )
        #
        #     view = Menu.add_item(Menu(), cards_select)
        # await interaction.response.send_message(view=view, embeds=embeds, ephemeral=True)
        await interaction.response.send_message("This command is currently disabled.")

async def setup(client: commands.Bot):
    await client.add_cog(GameOperationsCog(client))
