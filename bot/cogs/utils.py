from discord import Member, Guild, User
from discord.ext.commands import Bot

def has_role_or_higher(user: User | Member, rolename: str, guild: Guild | None) -> bool:
    if not isinstance(user, Member):
        return True

    if not guild:
        return True

    guild_rolenames = list(map(lambda x: x.name, guild.roles))

    if rolename not in guild_rolenames:
        return True

    highest = user.roles[-1].name
    return guild_rolenames.index(highest) >= guild_rolenames.index(rolename)

async def message_dev(bot: Bot, message: str):
    jojo = await bot.fetch_user(226054688368361474) # @jojodicus, bot dev
    await jojo.send(message)
