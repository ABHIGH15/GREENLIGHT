import os
import json
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from api.models import AnalysisRequest, ClearanceReport
from services.analysis_service import analysis_service
from tools.script_tools import extract_text_from_pdf, clean_screenplay_text

router = APIRouter(prefix="/api")

SAMPLE_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "sample_scripts", "landmine_script.txt"
)


@router.get("/sample")
async def get_sample_script():
    """Returns the sample screenplay with deliberate clearance landmines for demo testing."""
    if os.path.exists(SAMPLE_SCRIPT_PATH):
        with open(SAMPLE_SCRIPT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            return {"title": "THE APPRENTICE'S REVENGE", "script_text": content}
    return {
        "title": "SAMPLE SCRIPT",
        "script_text": "SCENE 1 - INT. OFFICE - DAY\nJULIAN enters..."
    }


@router.post("/analyze")
async def analyze_script(
    request: Optional[AnalysisRequest] = None,
    file: Optional[UploadFile] = File(None),
    script_text: Optional[str] = Form(None),
    script_title: Optional[str] = Form(None)
):
    """Kicks off the multi-agent clearance pipeline from uploaded PDF or raw text."""
    text_to_analyze = ""
    title_to_analyze = script_title

    if file:
        file_bytes = await file.read()
        if file.filename.lower().endswith(".pdf"):
            text_to_analyze = extract_text_from_pdf(file_bytes)
        else:
            text_to_analyze = file_bytes.decode("utf-8", errors="ignore")
        if not title_to_analyze:
            title_to_analyze = file.filename.rsplit(".", 1)[0].replace("_", " ").title()

    elif script_text:
        text_to_analyze = script_text

    elif request and request.script_text:
        text_to_analyze = request.script_text
        if request.script_title:
            title_to_analyze = request.script_title

    text_to_analyze = clean_screenplay_text(text_to_analyze)

    if not text_to_analyze or len(text_to_analyze.strip()) < 20:
        raise HTTPException(status_code=400, detail="Screenplay content must contain at least 20 characters.")

    analysis_id = await analysis_service.start_analysis(text_to_analyze, title_to_analyze)
    return {"analysis_id": analysis_id, "status": "started"}


@router.get("/report/{analysis_id}")
async def get_report(analysis_id: str):
    """Fetches the completed clearance report."""
    report = analysis_service.get_report(analysis_id)
    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not ready or not found.")
    return report


@router.get("/stream/{analysis_id}")
async def stream_pipeline_status(analysis_id: str):
    """Server-Sent Events (SSE) endpoint providing live agent pipeline updates."""
    queue = analysis_service.subscribe_events(analysis_id)

    async def event_generator():
        try:
            # Replay any already logged events
            existing = analysis_service.status_events.get(analysis_id, [])
            for evt in existing:
                yield f"data: {json.dumps(evt)}\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event.dict())}\n\n"
                    if event.completed:
                        break
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield ": keepalive\n\n"
        finally:
            analysis_service.unsubscribe_events(analysis_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
