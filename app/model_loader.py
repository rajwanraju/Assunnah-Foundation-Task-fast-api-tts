import logging

from transformers import AutoModel

logger = logging.getLogger(__name__)

_model = None
_model_device = None


def load_model(model_name: str, device: str = "cpu") -> AutoModel:
    global _model, _model_device

    if _model is not None:
        logger.info("Model already loaded, reusing existing instance")
        return _model

    logger.info(f"Loading IndicF5 model: {model_name} on {device}...")

    _model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    _model.to(device)
    _model.eval()

    _model_device = device
    logger.info("IndicF5 model loaded successfully")
    return _model


def get_model() -> AutoModel:
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def unload_model():
    global _model, _model_device
    if _model is not None:
        logger.info("Unloading IndicF5 model...")
        del _model
        _model = None
        _model_device = None
        logger.info("Model unloaded")
