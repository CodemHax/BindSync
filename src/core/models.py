from pydantic import BaseModel


class MessageCreate(BaseModel):
    text: str
    username: str = "API"
    reply_to_id: str = None


class MessageReply(BaseModel):
    text: str
    username: str = "API"

