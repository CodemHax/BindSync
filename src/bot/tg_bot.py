from telegram.ext import Application, MessageHandler, filters
from src.utils.bridge import is_from_discord, format_from_telegram
from src.database import store_functions


def tg_client(chat_id, token):
    async def handle_message(update, context):
        if not update.message or not update.message.text or update.message.chat_id != chat_id:
            return
        if is_from_discord(update.message.text):
            return
        username = update.message.from_user.full_name
        msg = format_from_telegram(username, update.message.text)
        bot_data = context.application.bot_data if context and context.application else {}
        forward_cb = bot_data.get('forward_to_discord')
        map_tg_to_dc = bot_data.get('map_tg_to_dc', {})
        map_dc_to_tg = bot_data.get('map_dc_to_tg', {})
        if not forward_cb:
            return

        reply_to_discord_message_id = None
        reply_to_internal_id = None
        reply_to_tg_id = None
        if update.message.reply_to_message:
            replied_tg_id = update.message.reply_to_message.message_id
            reply_to_tg_id = replied_tg_id
            reply_to_discord_message_id = map_tg_to_dc.get(replied_tg_id)
            try:
                m = await store_functions.find_by_tg_id(replied_tg_id)
                reply_to_internal_id = m["id"] if m else None
            except Exception as e:
                reply_to_internal_id = None

        tg_msg_id = update.message.message_id
        try:
            await store_functions.add_message(
                source='telegram',
                text=update.message.text,
                username=username,
                tg_msg_id=tg_msg_id,
                reply_to_tg_id=reply_to_tg_id,
                reply_to_dc_id=reply_to_discord_message_id,
                reply_to_id=reply_to_internal_id,
            )
        except Exception:
            pass

        try:
            dc_msg_id = await forward_cb(msg, reply_to_discord_message_id=reply_to_discord_message_id)
            if dc_msg_id:
                map_tg_to_dc[tg_msg_id] = dc_msg_id
                map_dc_to_tg[dc_msg_id] = tg_msg_id
                try:
                    await store_functions.set_dc_id_for_tg(tg_msg_id, int(dc_msg_id))
                except Exception:
                    pass
        except Exception:
            pass

    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
