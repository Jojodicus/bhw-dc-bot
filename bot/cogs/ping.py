from discord.ext.commands import Bot, Cog
from discord import Message, Embed, Color

from cogs.utils import has_role_or_higher


PING_IDS = {234720287449546753}
TITLE = "Ben pingen"
MESSAGE = """Bitte beachte, dass es nicht erwünscht ist, Ben in Nachrichten zu erwähnen. Er erhält täglich viele Pings und Privatnachrichten und kann nicht jedem antworten. Wenn du Ben kontaktieren möchtet, solltest du das über den Twitch-Chat tun.
Wir bitten daher, Ben (wenn überhaupt) nur in dringlichen Situationen zu pingen, oder wenn dies explizit gewünscht ist. Weitere Informationen dazu findest du im <#925137616481947678>"""

ALLOWED_ROLE = "Platin"


class Ping(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if has_role_or_higher(message.author, ALLOWED_ROLE, message.guild):
            return

        for id in PING_IDS:
            if f"<@{id}>" in message.content:
                embed = Embed(title=TITLE, description=MESSAGE, color=Color.blurple())
                await message.reply(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Ping(bot))
