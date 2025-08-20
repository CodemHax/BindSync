TG_TAG = "[TG]"
DC_TAG = "[DC]"


def is_from_telegram(text):
    return text.startswith(TG_TAG)


def is_from_discord(text):
    return text.startswith(DC_TAG)


def format_from_telegram(username, text):
    return f"{TG_TAG} {username}: {text}"


def format_from_discord(display_name, text):
    return f"{DC_TAG} {display_name}: {text}"


async def forward_to_discord(dbot, channel_id, message, logger=None):
    channel = dbot.get_channel(channel_id)
    if not channel:
        if logger:
            logger.error("Discord channel not found: ", channel_id)
        return
    try:
        await channel.send(message)
    except Exception as e:
        if logger:
            logger.exception("Failed to send message to Discord:", e)


async def forward_to_telegram(tbot, chat_id, message, logger=None):
    try:
        await tbot.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        if logger:
            logger.exception("Failed to send message to Telegram:", e)


async def forward_to_discord_with_reply(dbot, channel_id, message, reply_to_discord_message_id=None, logger=None):
    channel = dbot.get_channel(channel_id)
    if not channel:
        if logger:
            logger.error("Discord channel not found: ", channel_id)
        return None
    try:
        if reply_to_discord_message_id:
            try:
                ref_msg = await channel.fetch_message(reply_to_discord_message_id)
                sent = await ref_msg.reply(message)
            except Exception:
                sent = await channel.send(message)
        else:
            sent = await channel.send(message)
        return getattr(sent, "id", None)
    except Exception as e:
        if logger:
            logger.exception("Failed to send message to Discord:", e)
        return None


async def forward_to_telegram_with_reply(tbot, chat_id, message, reply_to_telegram_message_id=None, logger=None):
    try:
        sent = await tbot.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_to_message_id=reply_to_telegram_message_id,
        )
        return getattr(sent, "message_id", None)
    except Exception as e:
        if logger:
            logger.exception("Failed to send message to Telegram:", e)
        return None
