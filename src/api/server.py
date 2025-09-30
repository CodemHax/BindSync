from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from src.core.models import MessageCreate, MessageReply
from src.database import store_functions
from src.utils.bridge import fwd_to_tg_rply, fwd_dd_with_reply

app = FastAPI(title="BindSync", version="3.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tbot = None
dbot = None
cfg = None
map_tg_to_dc = None
map_dc_to_tg = None


def set_runtime(tb, db, config, tg_dc_map, dc_tg_map):
    global tbot, dbot, cfg, map_tg_to_dc, map_dc_to_tg
    tbot = tb
    dbot = db
    cfg = config
    map_tg_to_dc = tg_dc_map
    map_dc_to_tg = dc_tg_map


@app.get("/messages")
async def get_messages(limit: int = 100, offset: int = 0):
    limit = max(1, min(200, limit))
    offset = max(0, offset)
    messages = await store_functions.list_messages(limit=limit, offset=offset)
    print(messages)
    return {"messages": messages}


@app.get("/messages/{message_id}")
async def get_message(message_id: str):
    message = await store_functions.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@app.post("/messages")
async def create_message(msg: MessageCreate):
    msg_id = await store_functions.add_message(
        source='api',
        text=msg.text,
        username=msg.username,
        reply_to_id=msg.reply_to_id
    )

    reply_to_tg_id = None
    reply_to_dc_id = None

    if msg.reply_to_id:
        orig_msg = await store_functions.get_message(msg.reply_to_id)
        if orig_msg:
            reply_to_tg_id = orig_msg.get("tg_msg_id")
            reply_to_dc_id = orig_msg.get("dc_msg_id")

    formatted_msg = f"[API] {msg.username}: {msg.text}"

    tg_msg_id = None
    if tbot and cfg and "telegram_chat_id" in cfg:
        tg_msg_id = await fwd_to_tg_rply(
            tbot, cfg["telegram_chat_id"], formatted_msg,
            msg_id=reply_to_tg_id
        )
        if tg_msg_id:
            await store_functions.set_tg_msg_id(msg_id, int(tg_msg_id))

    dc_msg_id = None
    if dbot and cfg and "discord_channel_id" in cfg:
        dc_msg_id = await fwd_dd_with_reply(
            dbot, cfg["discord_channel_id"], formatted_msg,
            message_id=reply_to_dc_id
        )
        if dc_msg_id:
            await store_functions.set_dc_msg_id(msg_id, int(dc_msg_id))

    if tg_msg_id and dc_msg_id and map_tg_to_dc is not None and map_dc_to_tg is not None:
        map_tg_to_dc[int(tg_msg_id)] = int(dc_msg_id)
        map_dc_to_tg[int(dc_msg_id)] = int(tg_msg_id)

    return {"id": msg_id, "tg_msg_id": tg_msg_id, "dc_msg_id": dc_msg_id}


@app.post("/messages/{message_id}/reply")
async def reply_to_message(message_id: str, reply: MessageReply = Body(...)):
    orig_msg = await store_functions.get_message(message_id)
    if not orig_msg:
        raise HTTPException(status_code=404, detail="Original message not found")

    reply_id = await store_functions.add_message(
        source='api_reply',
        text=reply.text,
        username=reply.username,
        reply_to_id=message_id
    )

    formatted_reply = f"[API] {reply.username}: {reply.text}"

    tg_msg_id = None
    dc_msg_id = None

    if tbot and cfg and "telegram_chat_id" in cfg and orig_msg.get("tg_msg_id"):
        tg_msg_id = await fwd_to_tg_rply(
            tbot, cfg["telegram_chat_id"], formatted_reply,
            msg_id=orig_msg.get("tg_msg_id")
        )
        if tg_msg_id:
            await store_functions.set_tg_msg_id(reply_id, int(tg_msg_id))

    if dbot and cfg and "discord_channel_id" in cfg and orig_msg.get("dc_msg_id"):
        dc_msg_id = await fwd_dd_with_reply(
            dbot, cfg["discord_channel_id"], formatted_reply,
            message_id=orig_msg.get("dc_msg_id")
        )
        if dc_msg_id:
            await store_functions.set_dc_msg_id(reply_id, int(dc_msg_id))

    if tg_msg_id and dc_msg_id and map_tg_to_dc is not None and map_dc_to_tg is not None:
        map_tg_to_dc[int(tg_msg_id)] = int(dc_msg_id)
        map_dc_to_tg[int(dc_msg_id)] = int(tg_msg_id)

    return {"id": reply_id, "tg_msg_id": tg_msg_id, "dc_msg_id": dc_msg_id}


@app.get("/health")
async def health_check():
    """Health check endpoint to verify runtime initialization"""
    return {
        "status": "ok",
        "runtime": {
            "tbot_initialized": tbot is not None,
            "dbot_initialized": dbot is not None,
            "config_loaded": cfg is not None,
            "maps_initialized": map_tg_to_dc is not None and map_dc_to_tg is not None,
            "telegram_chat_id": cfg.get("telegram_chat_id") if cfg else None,
            "discord_channel_id": cfg.get("discord_channel_id") if cfg else None
        }
    }


# @app.get("/")
# async def serve_frontend():
#     """Serve the frontend HTML file"""
#     frontend_path = os.path.join(get_root(), "frontend", "index.html")
#     if os.path.exists(frontend_path):
#         return FileResponse(frontend_path)
#     else:
#         raise HTTPException(status_code=404, detail="Frontend not found")
