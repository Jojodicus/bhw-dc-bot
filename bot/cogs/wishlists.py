from discord.ext.commands import Bot, Cog
from discord import Message, Embed, Color
from aiohttp import ClientSession
from dataclasses import dataclass
import re
import os

from cogs.utils import message_dev, reply_embed


@dataclass
class ReplyContext:
    pattern: re.Pattern[str]
    title: str
    message: str

LOCAL = ReplyContext(
    pattern=re.compile(r'https?://geizhals..?.?/wishlists/local-[0-9]+'),
    title='Lokale Geizhals-Liste',
    message='''Diese Wunschliste ist eine lokale Wunschliste. Damit auch andere darauf zugreifen können muss diese **öffentlich** und in deinem **Account** hinterlegt sein.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>''',
)

PRIVATE = ReplyContext(
    pattern=re.compile(r'https?://geizhals..?.?/wishlists/[0-9]+'),
    title='Private Geizhals-Liste',
    message='''Diese Wunschliste ist eine private Wunschliste. Damit auch andere darauf zugreifen können muss diese **öffentlich** sein.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>''',
)

OVERVIEW = ReplyContext(
    pattern=re.compile(r'https?://geizhals..?.?/wishlists(?!/[0-9]+)'),
    title='Geizhals-Listen',
    message='''Du hast hier nur die Wunschlisten-Übersicht verlinkt. Wenn du einzelne Wunschlisten teilen möchtest, musst du diese einzeln verlinken.
Eine Anleitung zum Erstellen von Geizhals-Listen findest du hier: <#934229012069376071>''',
)

SUB_PATTERN = re.compile(r'https?://geizhals..?.?/wishlists/')


class Wishlists(Cog):
    def __init__(self, bot: Bot, api: str):
        self.bot = bot
        self.api = api
        self.session = ClientSession(headers={'cookie': self.api})

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        locals = LOCAL.pattern.findall(message.content)
        if locals:
            await reply_embed(message, LOCAL.title, LOCAL.message)
            return

        # private lists
        private = PRIVATE.pattern.findall(message.content)
        for link in private:
            page = SUB_PATTERN.sub('https://geizhals.de/api/usercontent/v0/wishlist/', link)
            async with self.session.get(page) as r:
                status = r.status
                data = await r.text()
            if status == 400 or 'private wishlist' in data:
                await reply_embed(message, PRIVATE.title, PRIVATE.message)
                return
            if r'{"code":403,"error":"Authentication failed"}' in data:
                await message_dev(self.bot, f'API Cookie für Geizhals ist abgelaufen, bitte erneuern')
                # TODO: DM to bot sets new api cookie

        # only overview to lists
        overview = OVERVIEW.pattern.findall(message.content)
        if overview:
            await reply_embed(message, OVERVIEW.title, OVERVIEW.message)

    @Cog.listener()
    async def cog_unload(self):
        await self.session.close()


async def setup(bot: Bot) -> None:
    api = os.getenv('GH_API_COOKIE')
    if not api:
        raise EnvironmentError('GH_API_COOKIE needed')
    await bot.add_cog(Wishlists(bot, api))
