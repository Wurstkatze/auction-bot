def register(bot):
    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == bot.user.id:
            return
        if str(payload.emoji) != "🔔":
            return

        auction = bot.auctions.get(payload.channel_id)
        if not auction:
            return
        if (
            not auction.last_bid_message
            or auction.last_bid_message.id != payload.message_id
        ):
            return

        pref_key = (payload.channel_id, payload.user_id)
        current = bot.notification_prefs.get(pref_key, False)
        bot.notification_prefs[pref_key] = not current

        channel = bot.get_channel(payload.channel_id)
        if channel:
            try:
                message = await channel.fetch_message(payload.message_id)
                if not current:
                    await message.channel.send(
                        f"<@{payload.user_id}> will now be DM'd if outbid!",
                        delete_after=5,
                    )
                else:
                    await message.channel.send(
                        f"<@{payload.user_id}> will no longer receive outbid notifications.",
                        delete_after=5,
                    )
            except:
                pass
