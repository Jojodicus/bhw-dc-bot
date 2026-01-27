import os

import aiohttp
import pytesseract
from cogs.utils import has_permissions
from discord import Color, Embed, Message
from discord.ext.commands import Bot, Cog, Context, command

TITLE = "Z Drücken um (f)TPM zurückzusetzen"
MESSAGE = "Der PC geht von einem amerikanischem Tastaturlayout aus, dort sind im Vergleich zum Deutschen Y und Z vertauscht.\nDer Hinweis zu Bitlocker ist für gewöhnlich nicht relevant, sollten weitere Schritte nötig sein, werden diese im weiteren Verlauf angezeigt."

tpmEmbed = Embed(title=TITLE, description=MESSAGE, color=Color.blurple())


SEARCH_STRINGS = (
    "Press Y to reset fTPM",
    "Press N to keep previous",
    "TPM record and continue",
)


class Tpm(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        async with aiohttp.ClientSession() as session:
            for attachment in message.attachments:
                if "image" not in (attachment.content_type or ""):
                    continue
                filename = f".cache/tesseract_{attachment.filename}"

                async with session.get(attachment.url) as resp:
                    with open(filename, "wb") as fd:
                        async for chunk in resp.content.iter_chunked(512):
                            fd.write(chunk)

                extracted = pytesseract.image_to_string(filename)
                os.remove(filename)

                for search in SEARCH_STRINGS:
                    if search in extracted:
                        await message.reply(embed=tpmEmbed)
                        return

    @command()
    async def tpm(self, ctx: Context) -> None:
        if not await has_permissions(ctx):
            return

        if ctx.message.reference:
            await ctx.channel.send(embed=tpmEmbed, reference=ctx.message.reference)
        else:
            await ctx.reply(embed=tpmEmbed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tpm(bot))
