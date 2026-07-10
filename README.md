# FastAPI TTS Service

Dedicated AI inference microservice for **IndicF5** text-to-speech.

Replaces Python subprocess spawning with a persistent model server. Model stays loaded in memory across requests — no per-inference reload overhead.

## Architecture

```
Express Worker ──HTTP──> FastAPI /generate ──> IndicF5 ──> Audio File
```

## Endpoints

| Method | Path                | Description                          |
| ------ | ------------------- | ------------------------------------ |
| GET    | `/health`           | Service health + model loaded status |
| GET    | `/voices`           | List available voices                |
| POST   | `/generate`         | Generate speech from text            |
| GET    | `/audio/{filename}` | Serve a generated audio file         |

### POST /generate

```json
{ "text": "আমি বাংলাদেশকে ভালোবাসি", "voice": "default" }
```

Response `200`:

```json
{
  "job_id": "uuid",
  "output_path": "/data/audio/uuid.wav",
  "duration_seconds": 1.23,
  "file_size_bytes": 48000,
  "sample_rate": 24000
}
```

## Prerequisites

1. Accept the [IndicF5 model license](https://huggingface.co/ai4bharat/IndicF5) on HuggingFace
2. Login via `huggingface-cli login` or set `HF_TOKEN` env var
3. Place reference prompt `.wav` files in `assets/prompts/`
4. Python 3.11+

## Quick Start (local)

```bash
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install git+https://github.com/ai4bharat/IndicF5.git
uvicorn app.main:app --reload
```

## Docker

### Build and run

```bash
docker build -t fastapi-tts .
docker run -p 8000:8000 \
  -v ./storage:/data/audio \
  -e HF_TOKEN=your_token_here \
  fastapi-tts
```

### docker-compose (recommended)

```bash
docker compose up -d --build
```

Exposes on port **8001** to avoid conflict with the Express API (port 8000).

### Volumes

- `./storage:/data/audio` — Generated audio files persist on host
- `huggingface_cache` (named volume) — Model weights cached across restarts

### Environment variables

| Variable            | Default             | Description                          |
| ------------------- | ------------------- | ------------------------------------ |
| `HOST`              | `0.0.0.0`           | Bind address                         |
| `PORT`              | `8000`              | Container port                       |
| `MODEL_NAME`        | `ai4bharat/IndicF5` | HuggingFace model ID                 |
| `DEVICE`            | `cpu`               | Inference device (`cpu` or `cuda`)   |
| `DTYPE`             | `float32`           | Model precision                      |
| `DEFAULT_LANGUAGE`  | `ben`               | Default language code                |
| `DEFAULT_VOICE`     | `default`           | Default voice profile                |
| `INFERENCE_TIMEOUT` | `120`               | Max inference seconds before timeout |
| `OUTPUT_DIR`        | `/data/audio`       | Audio output directory               |
| `LOG_LEVEL`         | `INFO`              | Logging level                        |
| `HF_TOKEN`          | —                   | HuggingFace auth token (required)    |

## Notes

- CPU inference on the 1B-parameter IndicF5 model typically takes 30–120s per request
- The Dockerfile installs a CPU-only PyTorch build to keep image size manageable (~3 GB vs ~7 GB with CUDA)
- For GPU inference, remove the `--index-url` flag so pip installs the CUDA-enabled build
