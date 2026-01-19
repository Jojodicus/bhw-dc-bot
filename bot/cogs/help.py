from discord.ext.commands import Bot, Cog, command, Context
from discord import Embed, Color

TITLE = "Hilfe"
TITLE_URL = "https://github.com/Jojodicus/bhw-dc-bot"
MESSAGE = "Klicke auf die Überschrift in dieser Nachricht um eine Übersicht über alle Befehle und Features zu bekommen."


class Help(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def help(self, ctx: Context) -> None:
        embed = Embed(
            title=TITLE, url=TITLE_URL, description=MESSAGE, color=Color.blurple()
        )
        await ctx.reply(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Help(bot))
