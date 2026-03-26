from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands

from discord.ext import commands, tasks # Add tasks
from datetime import datetime, timezone

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
        for channel_id, auction in list(self.auctions.items()):
            if auction.status == "SCHEDULED" and auction.start_time <= now:
                # Time to start!
                await self.trigger_scheduled_auction(auction)

    async def trigger_scheduled_auction(self, auction):
        # This function will call your existing logic to post the 
        # start message and move the auction to "ACTIVE"
        from src.commands.auctionCommands.startauction import run_start_logic
        await run_start_logic(self, auction)
