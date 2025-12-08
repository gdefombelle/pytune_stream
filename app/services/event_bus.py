# app/event_bus.py
import json
import asyncio
from typing import AsyncGenerator
from pytune_configuration.redis_config import get_redis_client

CHANNEL = "pytune:diagnosis_events"


async def publish_event(event: dict):
    """Called by another backend service to broadcast an event."""
    redis = await get_redis_client()
    await redis.publish(CHANNEL, json.dumps(event))


async def event_stream() -> AsyncGenerator[dict, None]:
    """
    Async generator used by SSE endpoints.
    Yields decoded JSON events.
    """
    redis = await get_redis_client()
    pubsub = redis.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])
            yield data
        except Exception:
            continue