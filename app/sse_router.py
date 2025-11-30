# app/sse_router.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
from app.event_bus import event_stream

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