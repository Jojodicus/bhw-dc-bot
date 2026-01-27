from discord import Color, Embed, Guild, Member, User
from discord.ext.commands import Bot, Context


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


ALLOWED_ROLE = "Silber"
PERMISSION_DENIED_TITLE = "Unzureichendes Level"
PERMISSION_DENIED_MESSAGE = "Du musst mindestens {} sein um diesen Befehl zu verwenden."


async def has_permissions(ctx: Context, role: str = ALLOWED_ROLE):
    if not has_role_or_higher(ctx.author, role, ctx.guild):
        embed = Embed(
            title=PERMISSION_DENIED_TITLE,
            description=PERMISSION_DENIED_MESSAGE.format(role),
            color=Color.blurple(),
        )
        await ctx.reply(embed=embed)
        return False
    return True


async def message_dev(bot: Bot, message: str):
    jojo = await bot.fetch_user(226054688368361474)  # @jojodicus, bot dev
    await jojo.send(message)
