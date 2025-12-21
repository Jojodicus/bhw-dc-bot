from discord import Member, Guild, User

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
