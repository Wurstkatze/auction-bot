import discord
from discord import app_commands
import database
from src.helperFunctions.isAdmin import isAdmin


def register(bot):
    @bot.tree.command(name="addpoints", description="Add points to a user")
    @app_commands.guild_only()
    @app_commands.describe(user="The user to reward", amount="Number of points")
    async def addpoints(
        interaction: discord.Interaction, user: discord.Member, amount: int
    ):
        if not await isAdmin(interaction):
            return

        database.add_points(user.id, amount)
        await interaction.response.send_message(
            f"✅ Added {amount} points to {user.mention}."
        )
