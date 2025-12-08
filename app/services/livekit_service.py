from livekit import api
from pytune_configuration import config, SimpleConfig

config = config or SimpleConfig()

API_KEY = config.LIVEKIT_API_KEY
API_SECRET = config.LIVEKIT_API_SECRET
ADMIN_URL = config.LIVEKIT_ADMIN_URL

lk = api.LiveKitAPI(API_KEY, API_SECRET, ADMIN_URL)

async def create_room_if_not_exists(room_name: str):
    rooms_resp = await lk.room.list_rooms()   # type: ignore
    for r in rooms_resp.rooms:
        if r.name == room_name:
            return r

    req = api.CreateRoomRequest(name=room_name)
    room = await lk.room.create_room(req)     # type: ignore
    return room

def create_join_token(identity: str, room: str):
    at = api.AccessToken(API_KEY, API_SECRET)
    grant = api.VideoGrants(room_join=True, room=room)
    at.add_grant(grant)                       # type: ignore
    return at.to_jwt()