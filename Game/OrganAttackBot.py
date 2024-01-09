import logging

import discord
from discord.ext import commands
from dotenv import dotenv_values

class OrganAttackBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)

        self.cogs_list = ["GameInitializationCog", ""]

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        # await self.tree.sync(guild=MY_GUILD)
        for ext in self.cogs_list:
            await self.load_extension(ext)

config = dotenv_values(".env")['ORGAN_ATTACK_BOT_TOKEN']
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
MY_GUILD = discord.Object(id=706518159984951337)
log_level = logging.DEBUG

intents_config = discord.Intents.all()
bot = OrganAttackBot(intents=intents_config)
