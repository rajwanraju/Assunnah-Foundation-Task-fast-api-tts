import asyncio
import json
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.model_loader import get_model
from app.inference import generate_speech, MAX_TEXT_LENGTH

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "prompts"
TRANSCRIPTS_PATH = ASSETS_DIR / "transcripts.json"

if not TRANSCRIPTS_PATH.exists():
    _voices_db: dict = {}
else:
    with open(TRANSCRIPTS_PATH) as f:
        _voices_db: dict = json.load(f)


class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH)
    voice: str = Field(default="default", max_length=50)
    filename: str | None = Field(default=None, max_length=255, description="Desired output filename (e.g. job-123.wav). Auto-generated if omitted.")


class GenerateResponse(BaseModel):
    job_id: str
    output_path: str
    duration_seconds: float
    file_size_bytes: int
    sample_rate: int


@router.get("/voices")
async def list_voices():
    return {"voices": list(_voices_db.keys())}


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    file_path = Path(settings.output_dir) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(file_path), media_type="audio/wav", filename=filename)


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    voice = req.voice or settings.default_voice

    if voice not in _voices_db:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown voice '{voice}'. Available: {list(_voices_db.keys())}",
        )

    voice_config = _voices_db[voice]
    ref_audio_path = str(ASSETS_DIR / voice_config["audio"])
    ref_text = voice_config["transcript"]

    job_id = str(uuid.uuid4())
    output_filename = req.filename or f"{job_id}.wav"
    output_path = str(Path(settings.output_dir) / output_filename)

    try:
        model = get_model()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, generate_speech, req.text, ref_audio_path, ref_text, output_path, settings.inference_timeout
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        logger.exception("Inference failed")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    return GenerateResponse(
        job_id=job_id,
        output_path=result["output_path"],
        duration_seconds=result["duration_seconds"],
        file_size_bytes=result["file_size_bytes"],
        sample_rate=result["sample_rate"],
    )
