from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio

from discord.ext import commands, tasks
from datetime import datetime, timezone

from database import get_pending_auctions, remove_scheduled_auction
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
        self.check_scheduled_auctions.start() # Start the loop
        await self.tree.sync()
        print(f"Synced commands for {self.user}")

    @tasks.loop(seconds=60) # Check every minute
    async def check_scheduled_auctions(self):
        now = datetime.now(timezone.utc)
        pending = get_pending_auctions() # Look in the database

        for row in pending:
            # Unpack the database row
            db_id, channel_id, seller_id, item, duration_str, start_price_str, min_inc_str, img_url, start_t_str, currency = row
            start_t = datetime.fromisoformat(start_t_str).replace(tzinfo=timezone.utc)

            # If the scheduled time has arrived AND the channel isn't busy
            if now >= start_t:
                if channel_id not in self.auctions:
                    try:
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
                        remove_scheduled_auction(db_id)
                        
                    except Exception as e:
                        print(f"Failed to auto-start scheduled auction for {item}: {e}")
                else:
                    # If channel is currently busy, it will just wait and try again next minute!
                    print(f"Channel {channel_id} is busy. Waiting to start scheduled auction: {item}")
