# app/services/event_bus.py
import json
from typing import AsyncGenerator
from pytune_configuration.redis_config import get_redis_client

CHANNEL = "pytune:events"  # ✅ générique

# {
#   "type": "status",
#   "scope": "identify_pro",
#   "session_id": "uuid",
#   "message": "Analyzing keyboard…",
#   "payload": {}
# }

async def publish_event(event: dict):
    """
    Publish a PyTune realtime event to Redis.
    """
    redis = await get_redis_client()
    await redis.publish(CHANNEL, json.dumps(event))

async def event_stream() -> AsyncGenerator[dict, None]:
    """
    Async generator for SSE stream.
    """
    redis = await get_redis_client()
    pubsub = redis.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            yield json.loads(message["data"])
        except Exception:
            continue