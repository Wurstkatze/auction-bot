import discord
from discord import app_commands
import database
from src.helperFunctions.isAdmin import isAdmin


def register(bot):

    @bot.tree.command(name="removepoints", description="Remove points from a user")
    @app_commands.guild_only()
    @app_commands.describe(user="The user", amount="Number of points")
    async def removepoints(
        interaction: discord.Interaction, user: discord.Member, amount: int
    ):
        if not await isAdmin(interaction):
            return

        if database.remove_points(user.id, amount):
            await interaction.response.send_message(
                f"✅ Removed {amount} points from {user.mention}."
            )
        else:
            await interaction.response.send_message(
                f"❌ {user.mention} doesn't have enough points.", ephemeral=True
            )
