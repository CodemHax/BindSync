from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from src.database import store_functions
from src.utils.bridge import forward_to_telegram_with_reply, forward_to_discord_with_reply

app = FastAPI(title="BindSync", version="1.0.0")

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


class MessageCreate(BaseModel):
    text: str
    username: str = "API"
    reply_to_id: str = None


class MessageReply(BaseModel):
    text: str
    username: str = "API"


def set_runtime(tb, db, config, tg_dc_map, dc_tg_map):
    global tbot, dbot, cfg, map_tg_to_dc, map_dc_to_tg
    tbot = tb
    dbot = db
    cfg = config
    map_tg_to_dc = tg_dc_map
    map_dc_to_tg = dc_tg_map


@app.get("/messages")
async def get_messages(limit: int = 100, offset: int = 0):
    try:
        limit = max(1, min(500, limit))
        offset = max(0, offset)
        messages = await store_functions.list_messages(limit=limit, offset=offset)
        print(messages)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{message_id}")
async def get_message(message_id: str):
    try:
        message = await store_functions.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages")
async def create_message(msg: MessageCreate):
    try:
        msg_id = await store_functions.add_message(
            source='api',
            text=msg.text,
            username=msg.username,
            reply_to_id=msg.reply_to_id
        )

        reply_to_tg_id = None
        reply_to_dc_id = None

        if msg.reply_to_id:
            try:
                orig_msg = await store_functions.get_message(msg.reply_to_id)
                if orig_msg:
                    reply_to_tg_id = orig_msg.get("tg_msg_id")
                    reply_to_dc_id = orig_msg.get("dc_msg_id")
            except Exception:
                pass

        formatted_msg = f"[API] {msg.username}: {msg.text}"

        tg_msg_id = None
        if tbot and cfg and "telegram_chat_id" in cfg:
            try:
                tg_msg_id = await forward_to_telegram_with_reply(
                    tbot, cfg["telegram_chat_id"], formatted_msg,
                    reply_to_telegram_message_id=reply_to_tg_id
                )
                if tg_msg_id:
                    await store_functions.set_tg_msg_id(msg_id, int(tg_msg_id))
            except Exception:
                pass

        dc_msg_id = None
        if dbot and cfg and "discord_channel_id" in cfg:
            try:
                dc_msg_id = await forward_to_discord_with_reply(
                    dbot, cfg["discord_channel_id"], formatted_msg,
                    reply_to_discord_message_id=reply_to_dc_id
                )
                if dc_msg_id:
                    await store_functions.set_dc_msg_id(msg_id, int(dc_msg_id))
            except Exception:
                pass

        if tg_msg_id and dc_msg_id and map_tg_to_dc is not None and map_dc_to_tg is not None:
            map_tg_to_dc[int(tg_msg_id)] = int(dc_msg_id)
            map_dc_to_tg[int(dc_msg_id)] = int(tg_msg_id)

        return {"id": msg_id, "tg_msg_id": tg_msg_id, "dc_msg_id": dc_msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/{message_id}/reply")
async def reply_to_message(message_id: str, reply: MessageReply = Body(...)):
    try:
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
            try:
                tg_msg_id = await forward_to_telegram_with_reply(
                    tbot, cfg["telegram_chat_id"], formatted_reply,
                    reply_to_telegram_message_id=orig_msg.get("tg_msg_id")
                )
                if tg_msg_id:
                    await store_functions.set_tg_msg_id(reply_id, int(tg_msg_id))
            except Exception:
                pass

        if dbot and cfg and "discord_channel_id" in cfg and orig_msg.get("dc_msg_id"):
            try:
                dc_msg_id = await forward_to_discord_with_reply(
                    dbot, cfg["discord_channel_id"], formatted_reply,
                    reply_to_discord_message_id=orig_msg.get("dc_msg_id")
                )
                if dc_msg_id:
                    await store_functions.set_dc_msg_id(reply_id, int(dc_msg_id))
            except Exception:
                pass

        if tg_msg_id and dc_msg_id and map_tg_to_dc is not None and map_dc_to_tg is not None:
            map_tg_to_dc[int(tg_msg_id)] = int(dc_msg_id)
            map_dc_to_tg[int(dc_msg_id)] = int(tg_msg_id)

        return {"id": reply_id, "tg_msg_id": tg_msg_id, "dc_msg_id": dc_msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_project_root():
    current_file = os.path.abspath(__file__)
    api_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(api_dir)
    return os.path.dirname(src_dir)


@app.get("/")
async def test():
    frontend_path = os.path.join(get_project_root(), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Frontend file not found."}
