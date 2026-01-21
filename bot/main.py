import discord
from discord.ext import commands
import os
import asyncio
from pathlib import Path


COGS = {
    "ping",
    "react",
    "wishlists",
    "meta",
    "help",
    "tpm",
    "benchmark",
}


class BhwBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.remove_command("help")
        for extension in COGS:
            await self.load_extension(f"cogs.{extension}")

    async def on_ready(self) -> None:
        print(f"{self.user} is up and running on {len(self.guilds)} servers!")


async def main() -> None:
    Path(".cache").mkdir(exist_ok=True)
    token = os.getenv("BHW_TOKEN")
    if not token:
        raise EnvironmentError("You need to set BHW_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True
    async with BhwBot(command_prefix="%", intents=intents) as bot:
        await bot.start(token)


asyncio.run(main())
