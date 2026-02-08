# app/sse_router.py
from datetime import time
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.services.event_bus import event_stream, publish_event

router = APIRouter(prefix="/events")


async def sse_generator():
    async for event in event_stream():
        payload = json.dumps(event, ensure_ascii=False)

        yield (
            f"event: {event.get('type','analysis')}\n"
            f"data: {payload}\n\n"
        )


@router.get("/sse")
async def sse():
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.post("/push")
async def push_event(event: dict = Body(...)):
    """
    Push an event to the PyTune SSE stream.
    Used by other backend services.
    """
    if "type" not in event:
        raise HTTPException(status_code=400, detail="Missing event.type")

    event.setdefault("ts", time.time())

    await publish_event(event)
    return {"status": "ok"}