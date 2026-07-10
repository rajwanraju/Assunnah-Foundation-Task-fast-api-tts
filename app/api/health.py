from fastapi import APIRouter
import app.model_loader

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    model_loaded = app.model_loader._model is not None
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "service": "fastapi-tts",
        "model": "ai4bharat/IndicF5",
    }
