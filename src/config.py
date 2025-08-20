import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


def load_config():
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    tg_chat = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
    dc_token = os.getenv("DISCORD_BOT_TOKEN", "")
    dc_channel = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

    missing = []
    if not tg_token:
        missing.append("TELEGRAM_TOKEN|TELEGRAM_BOT_TOKEN")
    if tg_chat == 0:
        missing.append("TELEGRAM_CHAT_ID")
    if not dc_token:
        missing.append("DISCORD_TOKEN|DISCORD_BOT_TOKEN")
    if dc_channel == 0:
        missing.append("DISCORD_CHANNEL_ID")
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))

    return {
        "telegram_token": tg_token,
        "telegram_chat_id": tg_chat,
        "discord_token": dc_token,
        "discord_channel_id": dc_channel,
    }
