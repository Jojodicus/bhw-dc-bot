from discord.ext.commands import Bot, Cog
from discord import Message
import random

class React(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not self.bot.user:
            return

        if self.bot.user.id not in map(lambda x: x.id, message.mentions):
            return

        if not message.guild:
            return

        if not message.guild.emojis:
            return

        # react with random emote
        emoji = random.choice(message.guild.emojis)
        await message.add_reaction(emoji)

async def setup(bot: Bot) -> None:
    await bot.add_cog(React(bot))
