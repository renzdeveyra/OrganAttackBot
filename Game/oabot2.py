import discord

import game
from utils import generate_attack_embeds, display_organs

class TrueBot:
    def __init__(self, client, config, handler, logging_debug):
        self.client = client
        self.config = config
        self.handler = handler
        self.logging_debug = logging_debug
        self.game_key_ref = ''
        self.games_registry = {}
        self.players_list = {}

    async def on_ready(self):
        print(f'Logged in as {self.client.user} (ID: {self.client.user.id})')
        print('------')

    async def join(self, interaction: discord.Interaction):
        user_mention = interaction.user.mention
        user_name = interaction.user.name
        if user_name in self.players_list:
            print("this")
            await interaction.response.send_message(f"Last time I checked, you already joined {user_name}...")
            return
        if len(self.players_list) == 6:
            await interaction.response.send_message(f"There's already 6 of you! (,,>﹏<,,)\n"
                                                    f'Type `/players` to see for yourself (¬_¬")')
            return
        else:
            self.players_list[user_mention] = user_name
            print(f"Added {user_name} as {user_mention}")
            await interaction.response.send_message(f"Hello, {user_mention}\n"
                                                    "You have joined the game! (✿◠‿◠)")

    def activate(self):
        self.client.event(self.on_ready)
        self.client.tree.command(name='join', description='Join a game.')(self.join)