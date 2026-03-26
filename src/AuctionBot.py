from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio

import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

import database
from src.auctionFunctions.trigger_auction import trigger_auction
from src.helperFunctions.parse_duration import parse_duration
from src.helperFunctions.parse_amount import parse_amount

if TYPE_CHECKING:
    from src.Auction import Auction
    from src.ItemDropdownView import ItemDropdownView

class AuctionBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)
        self.auctions: dict[int, Auction] = {}
        self.notification_prefs: dict[tuple[int, int], bool] = {}
        self.active_views: list[ItemDropdownView] = []

    async def setup_hook(self):
        self.check_scheduled_auctions.start() 
        await self.tree.sync()
        print(f"Synced commands for {self.user}")

    # --- CATCH BUTTON CLICKS FOR NOTIFICATIONS ---
    async def on_interaction(self, interaction: discord.Interaction):
        await super().on_interaction(interaction) # Ensure commands still work
        
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id", "")
            if custom_id.startswith("sched_bell_"):
                db_id = int(custom_id.split("_")[2])
                
                # Toggle in DB
                is_added = database.toggle_scheduled_notif(db_id, interaction.user.id)
                if is_added:
                    await interaction.response.send_message("✅ You will get a DM when this auction starts!", ephemeral=True)
                else:
                    await interaction.response.send_message("🔕 You will no longer be notified for this auction.", ephemeral=True)

    # --- BACKGROUND LOOP ---
    @tasks.loop(seconds=60) 
    async def check_scheduled_auctions(self):
        now = datetime.now(timezone.utc)
        pending = database.get_pending_auctions() 

        for row in pending:
            db_id, channel_id, seller_id, item, duration_str, start_price_str, min_inc_str, img_url, start_t_str, currency = row
            start_t = datetime.fromisoformat(start_t_str).replace(tzinfo=timezone.utc)

            if now >= start_t:
                if channel_id not in self.auctions:
                    try:
                        # --- SEND DMs TO SUBSCRIBERS ---
                        subscribers = database.get_scheduled_notifs(db_id)
                        for sub_id in subscribers:
                            try:
                                user = self.get_user(sub_id) or await self.fetch_user(sub_id)
                                await user.send(f"🔔 **The auction for {item} is starting NOW!**\nJump in here: <#{channel_id}>")
                            except: 
                                pass # Ignore if they have DMs blocked
                                
                        # 1. Fetch Discord objects
                        channel = self.get_channel(channel_id) or await self.fetch_channel(channel_id)
                        seller = channel.guild.get_member(seller_id) or await channel.guild.fetch_member(seller_id)
                        
                        # 2. Parse the strings back into usable values
                        delta = parse_duration(duration_str)
                        start_val, _ = parse_amount(start_price_str)
                        min_inc_val, _ = parse_amount(min_inc_str)

                        # 3. Fire the auction using the shared helper function!
                        await trigger_auction(
                            bot=self, channel=channel, seller=seller, item_name=item, 
                            delta=delta, start_val=start_val, min_inc_val=min_inc_val, 
                            currency=currency, image_url=img_url
                        )
                        
                        # 4. Remove from database so it doesn't start twice
                        database.remove_scheduled_auction(db_id)
                        
                    except Exception as e:
                        print(f"Failed to auto-start scheduled auction for {item}: {e}")
                else:
                    print(f"Channel {channel_id} is busy. Waiting to start scheduled auction: {item}")
