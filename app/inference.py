import logging
import time
import threading
import concurrent.futures
import torch
from pathlib import Path
import numpy as np
import soundfile as sf

from app.model_loader import get_model

logger = logging.getLogger(__name__)

SAMPLE_RATE = 24000
MAX_TEXT_LENGTH = 1000

_inference_lock = threading.Lock()


def generate_speech(
    text: str,
    ref_audio_path: str,
    ref_text: str,
    output_path: str,
    timeout: int = 120,
) -> dict:
    if not text.strip():
        raise ValueError("Text must not be empty")

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters")

    if not Path(ref_audio_path).exists():
        raise FileNotFoundError(f"Reference audio not found: {ref_audio_path}")

    model = get_model()
    logger.info(f"Generating speech for text ({len(text)} chars)...")
    start = time.time()

    def _run_inference():
        with _inference_lock:
            with torch.inference_mode():
                return model(text, ref_audio_path=ref_audio_path, ref_text=ref_text)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_run_inference)
        try:
            audio = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Inference timed out after {timeout}s")

    elapsed = time.time() - start
    logger.info(f"Inference completed in {elapsed:.2f}s")

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0

    sf.write(str(output_path_obj), np.array(audio, dtype=np.float32), samplerate=SAMPLE_RATE)

    file_size = output_path_obj.stat().st_size
    logger.info(f"Audio saved to {output_path} ({file_size} bytes, {SAMPLE_RATE} Hz)")

    return {
        "output_path": str(output_path_obj.resolve()),
        "duration_seconds": round(elapsed, 2),
        "file_size_bytes": file_size,
        "sample_rate": SAMPLE_RATE,
    }
