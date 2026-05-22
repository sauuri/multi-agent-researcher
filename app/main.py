import json
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.graph import ResearchState, graph

app = FastAPI(title="Multi-Agent Researcher", version="1.0.0")

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ResearchRequest(BaseModel):
    topic: str


@app.get("/")
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/research")
async def research(req: ResearchRequest):
    async def generate():
        try:
            yield _sse({"type": "start", "message": f"'{req.topic}' 리서치를 시작합니다..."})

            initial: ResearchState = {
                "topic": req.topic,
                "queries": [],
                "results": [],
                "analysis": "",
                "report": "",
                "logs": [],
            }

            async for chunk in graph.astream(initial, stream_mode="updates"):
                for node_name, updates in chunk.items():
                    for log in updates.get("logs", []):
                        yield _sse({"type": "log", "node": node_name, "message": log})

                    if updates.get("report"):
                        yield _sse({"type": "report", "content": updates["report"]})

            yield _sse({"type": "done"})

        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
