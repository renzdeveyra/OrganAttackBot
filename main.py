import logging

import discord
from discord import app_commands
from dotenv import dotenv_values

import Game.oabot as bot

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

config = dotenv_values(".env")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

MY_GUILD = discord.Object(id=706518159984951337)

intents_config = discord.Intents.all()
client = MyClient(intents=intents_config)

if __name__ == "__main__":
    # run OABot
    # client.run(config['TOKEN1'], log_handler=handler, log_level=logging.DEBUG)
    bot.activate(client, config['TOKEN1'], handler, logging.DEBUG)

