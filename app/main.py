import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.model_loader import load_model, unload_model
from app.api.health import router as health_router
from app.api.generate import router as generate_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info(
        f"Starting FastAPI TTS service with model {settings.model_name} "
        f"on device={settings.device}"
    )

    try:
        load_model(settings.model_name, settings.device)
    except Exception as e:
        logger.error(f"Failed to load model at startup: {e}")
        raise

    yield

    logger.info("Shutting down FastAPI TTS service...")
    unload_model()


app = FastAPI(
    title="FastAPI TTS Service",
    description="Dedicated AI inference service for IndicF5 text-to-speech",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(generate_router)
