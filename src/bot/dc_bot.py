import discord
from src.utils.bridge import is_from_telegram, format_from_discord


def dd_client(channel_id):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print("Connected to Discord channel" if client.get_channel(channel_id) else "Discord: channel not found")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.channel.id != channel_id:
            return
        if is_from_telegram(message.content or ""):
            return

        msg = format_from_discord(message.author.display_name, message.content or "")
        forward_cb = getattr(client, 'forward_to_telegram', None)
        map_tg_to_dc = getattr(client, 'map_tg_to_dc', {})
        map_dc_to_tg = getattr(client, 'map_dc_to_tg', {})
        if not forward_cb:
            return


        reply_to_telegram_message_id = None
        ref = getattr(message, 'reference', None)
        if ref and getattr(ref, 'message_id', None):
            reply_to_telegram_message_id = map_dc_to_tg.get(ref.message_id)

        try:
            tg_msg_id = await forward_cb(msg, reply_to_telegram_message_id=reply_to_telegram_message_id)
            if tg_msg_id:
                dc_msg_id = message.id
                map_dc_to_tg[dc_msg_id] = tg_msg_id
                map_tg_to_dc[tg_msg_id] = dc_msg_id
        except Exception:
            pass

    return client

