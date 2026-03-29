import discord
from discord import app_commands
import database
from src.helperFunctions.isAdmin import isAdmin


def register(bot):

    @bot.tree.command(
        name="removeitem", description="Remove an item from the pool by ID"
    )
    @app_commands.guild_only()
    @app_commands.describe(item_id="The ID of the item to remove")
    async def removeitem(interaction: discord.Interaction, item_id: int):
        if not await isAdmin(interaction):
            return

        if database.remove_item(item_id):
            await interaction.response.send_message(f"✅ Item #{item_id} removed.")
        else:
            await interaction.response.send_message(
                f"❌ Item #{item_id} not found.", ephemeral=True
            )
