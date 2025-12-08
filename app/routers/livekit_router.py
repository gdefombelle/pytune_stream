from fastapi import APIRouter, Request, Header, HTTPException
import json
import hmac
import hashlib

from pytune_configuration import config, SimpleConfig
from app.services.livekit_service import create_join_token, create_room_if_not_exists

config = config or SimpleConfig()

router = APIRouter(prefix="/livekit", tags=["LiveKit"])

WEBHOOK_SECRET = config.LIVEKIT_API_SECRET

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

# ─────────────────────────────────────────────────────────────
# 1) WEBHOOK : LiveKit → PyTune Stream
# ─────────────────────────────────────────────────────────────
@router.post("/webhook")
async def livekit_webhook(
    request: Request,
    authorization: str | None = Header(default=None),
):
    raw_body = await request.body()
    body_text = raw_body.decode("utf-8", errors="ignore")

    print("===== LIVEKIT WEBHOOK RECEIVED =====")
    print("Authorization:", authorization)
    print("Raw body:", body_text)

    try:
        event = json.loads(body_text)
        print("Event type:", event.get("event"))
        print("Room:", event.get("room", {}).get("name"))
    except Exception as e:
        print("Error parsing JSON:", e)

    return {"ok": True}
# ─────────────────────────────────────────────────────────────
# 2) CREATE ROOM (backend)
# ─────────────────────────────────────────────────────────────
@router.post("/create-room")
async def create_room(data: dict):
    room_name = data.get("room_name")
    if not room_name:
        raise HTTPException(status_code=400, detail="Missing room_name")

    result = await create_room_if_not_exists(room_name)
    return {"ok": True, "room": result}

# ─────────────────────────────────────────────────────────────
# 3) GENERATE JOIN TOKEN (frontend calls this)
# ─────────────────────────────────────────────────────────────
@router.post("/token")
async def token(data: dict):
    identity = data.get("identity")
    room = data.get("room")

    if not identity or not room:
        raise HTTPException(status_code=400, detail="Missing identity or room")

    token = create_join_token(identity, room)
    return {"token": token, "url": config.get("LIVEKIT_URL")}