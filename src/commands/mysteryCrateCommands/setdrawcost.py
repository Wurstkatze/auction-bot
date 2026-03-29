import discord
from discord import app_commands
import database
from src.helperFunctions.isAdmin import isAdmin


def register(bot):

    @bot.tree.command(
        name="setdrawcost", description="Set the points required per draw"
    )
    @app_commands.guild_only()
    @app_commands.describe(amount="Points per draw")
    async def setdrawcost(interaction: discord.Interaction, amount: int):
        if not await isAdmin(interaction):
            return

        database.set_setting("draw_cost", str(amount))
        await interaction.response.send_message(f"✅ Draw cost set to {amount} points.")
