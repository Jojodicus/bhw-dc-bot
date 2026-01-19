from discord.ext.commands import Bot, Cog
from discord import Message, Embed, Color
from aiohttp import ClientSession
from dataclasses import dataclass
import re

from cogs.utils import message_dev


@dataclass
class ReplyContext:
    pattern: re.Pattern[str]
    title: str
    message: str


LOCAL = ReplyContext(
    pattern=re.compile(r"https?://geizhals..?.?/wishlists/local-[0-9]+"),
    title="Lokale Geizhals-Liste",
    message="""Diese Wunschliste ist eine lokale Wunschliste. Damit auch andere darauf zugreifen können muss diese **öffentlich** und in deinem **Account** hinterlegt sein.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>""",
)

PRIVATE = ReplyContext(
    pattern=re.compile(r"https?://geizhals..?.?/wishlists/[0-9]+"),
    title="Private Geizhals-Liste",
    message="""Diese Wunschliste ist eine private Wunschliste. Damit auch andere darauf zugreifen können muss diese **öffentlich** sein.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>""",
)

OVERVIEW = ReplyContext(
    pattern=re.compile(r"https?://geizhals..?.?/wishlists(?!/[0-9]+)"),
    title="Geizhals-Listen",
    message="""Du hast hier nur die Wunschlisten-Übersicht verlinkt. Wenn du einzelne Wunschlisten teilen möchtest, musst du diese einzeln verlinken.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>""",
)

SUB_PATTERN = re.compile(r"https?://geizhals..?.?/wishlists/")


class Wishlists(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.session = ClientSession()

    async def refresh_token(self) -> None:
        await self.session.get("https://geizhals.de/", headers={"User-Agent": "BHW"})

    async def scan_for_private(self, message: Message, attempts=1) -> bool:
        private = PRIVATE.pattern.findall(message.content)
        for link in private:
            page = SUB_PATTERN.sub(
                "https://geizhals.de/api/usercontent/v0/wishlist/", link
            )
            async with self.session.get(page) as r:
                status = r.status
                data = await r.text()
            if status == 400 or "private wishlist" in data:
                return True
            if r'{"code":403,"error":"Authentication failed"}' in data:
                if attempts <= 0:
                    await message_dev(
                        self.bot,
                        "API Cookie für Geizhals ist abgelaufen, bitte erneuern",
                    )
                else:
                    await self.refresh_token()
                    return await self.scan_for_private(message, attempts - 1)
        return False

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        # local lists
        locals = LOCAL.pattern.findall(message.content)
        if locals:
            embed = Embed(
                title=LOCAL.title, description=LOCAL.message, color=Color.blurple()
            )
            await message.reply(embed=embed)
            return

        # private lists
        if await self.scan_for_private(message):
            embed = Embed(
                title=PRIVATE.title, description=PRIVATE.message, color=Color.blurple()
            )
            await message.reply(embed=embed)
            return

        # only overview to lists
        overview = OVERVIEW.pattern.findall(message.content)
        if overview:
            embed = Embed(
                title=OVERVIEW.title,
                description=OVERVIEW.message,
                color=Color.blurple(),
            )
            await message.reply(embed=embed)

    async def cog_unload(self):
        await self.session.close()


async def setup(bot: Bot) -> None:
    cog = Wishlists(bot)
    await cog.refresh_token()
    await bot.add_cog(cog)
