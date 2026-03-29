import discord

import config


async def isAdmin(interaction: discord.Interaction) -> bool:
    """
    isAdmin MUST be called in a command with the `@app_commands.guild_only()` decorator.
    Discord will raise an Exception otherwise
    """
    # We assume we are in a guild context
    assert interaction.guild
    assert isinstance(interaction.user, discord.Member)

    # Check if the invoker has the required admin role
    if (
        discord.utils.get(interaction.guild.roles, name=config.discord.ADMIN_ROLE)
        not in interaction.user.roles
    ):
        await interaction.response.send_message(
            f"You need the **{config.discord.ADMIN_ROLE}** role to add items.",
            ephemeral=True,
        )
        return False

    return True
