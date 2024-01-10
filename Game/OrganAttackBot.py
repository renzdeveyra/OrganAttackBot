import discord
from discord.ext import commands
from colorama import Back, Fore, Style
import time

class OrganAttackBot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)

    async def setup_hook(self):
        # for ext in self.cogs_list:
        print(f"Setting up Game.GameInitializationCog...")
        await self.load_extension("Game.GameInitializationCog")

    async def on_ready(self):
        color_config = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime())
                        + Back.RESET + Fore.WHITE + Style.BRIGHT + " [OrganAttackBot]")
        print(color_config + " Logged in as " + Fore.YELLOW + self.user.name)
        print(color_config + " Bot ID " + Fore.YELLOW + str(self.user.id))
        synced = await self.tree.sync()
        print(color_config + " Slash CMDs Synced " + Fore.YELLOW + str(len(synced)) + " Commands" + Style.RESET_ALL)

intents_config = discord.Intents.all()

bot = OrganAttackBot(intents=intents_config)
