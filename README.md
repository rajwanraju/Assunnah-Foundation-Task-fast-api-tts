# FastAPI TTS Service

Dedicated AI inference microservice for **IndicF5** text-to-speech.

Replaces Python subprocess spawning with a persistent model server.

## Architecture

```
Express Worker ──HTTP──> FastAPI /generate ──> IndicF5 ──> Audio File
```

Model stays loaded in memory across requests: no per-inference reload overhead.

## Endpoints

| Method | Path        | Description                          |
| ------ | ----------- | ------------------------------------ |
| GET    | `/health`   | Service health + model loaded status |
| GET    | `/voices`   | List available voices                |
| POST   | `/generate` | Generate speech from text            |

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

## Quick Start

```bash
pip install -r requirements.txt
pip install git+https://github.com/ai4bharat/IndicF5.git
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t fastapi-tts .
docker run -p 8000:8000 -v ./storage:/data/audio fastapi-tts
```
