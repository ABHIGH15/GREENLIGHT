import os
import json
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from api.models import AnalysisRequest, ClearanceReport
from services.analysis_service import analysis_service
from tools.script_tools import extract_text_from_pdf, clean_screenplay_text

router = APIRouter(prefix="/api")

SAMPLE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "sample_scripts"
)
SAMPLE_SCRIPT_PATH = os.path.join(SAMPLE_DIR, "landmine_script.txt")


@router.get("/sample")
async def get_sample_script(preset: str = "flagship"):
    """Returns a sample screenplay benchmark preset for demo testing."""
    filename_map = {
        "flagship": ("landmine_script.txt", "THE APPRENTICE'S REVENGE"),
        "common": ("common_name_script.txt", "BLUEPRINT FOR AUTUMN"),
        "common_name": ("common_name_script.txt", "BLUEPRINT FOR AUTUMN"),
        "clean": ("clean_control_script.txt", "WHISPERS OF THE MEADOW"),
        "clean_control": ("clean_control_script.txt", "WHISPERS OF THE MEADOW"),
    }
    fname, title = filename_map.get(preset.lower(), ("landmine_script.txt", "THE APPRENTICE'S REVENGE"))
    target_path = os.path.join(SAMPLE_DIR, fname)
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            return {"title": title, "script_text": content}
    return {
        "title": title,
        "script_text": "TITLE: SAMPLE SCRIPT\n\nSCENE 1 - INT. STUDIO - DAY\nClearance demo script."
    }



MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_TEXT_LENGTH = 350_000  # ~50,000 words / ~120 screenplay pages
MIN_TEXT_LENGTH = 20
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".fountain", ".fdx"}


@router.post("/analyze")
async def analyze_script(
    request: Request,
    file: Optional[UploadFile] = File(None),
    script_text: Optional[str] = Form(None),
    script_title: Optional[str] = Form(None)
):
    """Kicks off the multi-agent clearance pipeline from uploaded PDF, multipart form, or JSON body."""
    text_to_analyze = ""
    title_to_analyze = script_title

    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            text_to_analyze = body.get("script_text", "")
            if not title_to_analyze and body.get("script_title"):
                title_to_analyze = body.get("script_title")
        except Exception:
            pass

    if not text_to_analyze and file:
        filename = file.filename or "uploaded_script"
        ext = os.path.splitext(filename)[1].lower()
        if ext and ext not in ALLOWED_EXTENSIONS:
            allowed_list = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported screenplay formats are: {allowed_list}."
            )

        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file exceeds the maximum limit of {MAX_FILE_SIZE // (1024 * 1024)}MB."
            )

        if ext == ".pdf":
            extracted = extract_text_from_pdf(file_bytes)
            if not extracted or len(extracted.strip()) < MIN_TEXT_LENGTH:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract readable screenplay text from the uploaded PDF. The file may be empty, corrupted, image-based/scanned, or password-protected."
                )
            text_to_analyze = extracted
        else:
            text_to_analyze = file_bytes.decode("utf-8", errors="ignore")

        if not title_to_analyze and file.filename:
            title_to_analyze = file.filename.rsplit(".", 1)[0].replace("_", " ").title()

    elif not text_to_analyze and script_text:
        text_to_analyze = script_text

    text_to_analyze = clean_screenplay_text(text_to_analyze)

    if not text_to_analyze or len(text_to_analyze.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Screenplay content must contain at least {MIN_TEXT_LENGTH} characters of readable text."
        )

    if len(text_to_analyze) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Screenplay text exceeds the maximum supported length of {MAX_TEXT_LENGTH:,} characters (~120 pages)."
        )

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
