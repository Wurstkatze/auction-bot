import discord
from discord import Member


async def get_guild_member(guild_channel: discord.TextChannel, member_id: int) -> Member:
    """
    Get a guild member (try cached, then API).
    Lets discord exceptions fall through.
    """
    return guild_channel.guild.get_member(
        member_id
    ) or await guild_channel.guild.fetch_member(member_id)
