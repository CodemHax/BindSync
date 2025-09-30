import logging
import asyncio
import uvicorn

from src.config import load_config
from src.bot.tg_bot import tg_client
from src.bot.dc_bot import dd_client
from src.database import database, store_functions
from src.api.server import app, set_runtime
from src.utils.bridge import (
    fwd_dd_with_reply as util_forward_dc_reply,
    fwd_to_tg_rply as util_forward_tg_reply,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bridge.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

async def main():
    cfg = load_config()

    await database.init_db(cfg["mongo_uri"], cfg["mongo_db"])
    await store_functions.configure()
    logger.info("Connected to MongoDB")

    map_tg_to_dc = {}
    map_dc_to_tg = {}

    tbot = tg_client(chat_id=cfg["telegram_chat_id"], token=cfg["telegram_token"])
    dbot = dd_client(channel_id=cfg["discord_channel_id"])

    async def fwd_to_dd(message, reply_to_discord_message_id=None):
        return await util_forward_dc_reply(
            dbot,
            cfg["discord_channel_id"],
            message,
            message_id=reply_to_discord_message_id,
        )

    async def forward_to_telegram(message, reply_to_telegram_message_id=None):
        return await util_forward_tg_reply(
            tbot,
            cfg["telegram_chat_id"],
            message,
            msg_id=reply_to_telegram_message_id,
        )

    tbot.bot_data['fwd_to_dd'] = fwd_to_dd
    tbot.bot_data['map_tg_to_dc'] = map_tg_to_dc
    tbot.bot_data['map_dc_to_tg'] = map_dc_to_tg

    setattr(dbot, 'forward_to_telegram', forward_to_telegram)
    setattr(dbot, 'map_tg_to_dc', map_tg_to_dc)
    setattr(dbot, 'map_dc_to_tg', map_dc_to_tg)

    set_runtime(tbot, dbot, cfg, map_tg_to_dc, map_dc_to_tg)

    config = uvicorn.Config(app, host=cfg["api_host"], port=cfg["api_port"], log_level="info")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())add

    async with tbot, dbot:
        logger.info("Starting Telegram bot polling...")
        await tbot.initialize()
        await tbot.start()
        logger.info("Starting Discord bot...")
        discord_task = asyncio.create_task(dbot.start(cfg["discord_token"]))
        polling_task = asyncio.create_task(tbot.updater.start_polling())
        await asyncio.gather(api_task, discord_task, polling_task)
