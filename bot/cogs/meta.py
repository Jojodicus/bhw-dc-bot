import re

from cogs.utils import has_permissions
from discord import Color, Embed, Message
from discord.ext.commands import Bot, Cog, Context, command

TITLE = "Metafrage"
TITLE_URL = "https://metafrage.de/"
MESSAGE = "Bitte keine Metafragen stellen. Formuliere dein konkretes Problem direkt, sonst wissen andere nicht, ob sie helfen können, und gute Antworten bleiben oft aus."

metaEmbed = Embed(
    title=TITLE, url=TITLE_URL, description=MESSAGE, color=Color.blurple()
)

PATTERN = re.compile(r"kennt sich (hier )?(wer|jemand|einer) mit [a-z A-Z]* aus *\?*")


class Meta(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        text = message.content.lower()
        finding = PATTERN.match(text)
        if finding and finding.group() == text:
            await message.reply(embed=metaEmbed)

    @command()
    async def meta(self, ctx: Context) -> None:
        if not await has_permissions(ctx):
            return

        if ctx.message.reference:
            await ctx.channel.send(embed=metaEmbed, reference=ctx.message.reference)
        else:
            await ctx.reply(embed=metaEmbed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Meta(bot))
