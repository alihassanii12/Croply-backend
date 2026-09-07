"""Client for the FastAPI inference microservice."""

import requests
from django.conf import settings


class InferenceError(Exception):
    """Raised when the inference service cannot produce a prediction."""


def predict_image(image_file):
    """Send an uploaded image to the inference service.

    Returns the parsed JSON payload:
    {
        "predicted_class": str,
        "plant": str,
        "disease": str,
        "confidence": float,
        "top_predictions": [{"class_name": str, "confidence": float}, ...],
    }
    """

    url = f'{settings.INFERENCE_API_URL}/predict'

    image_file.seek(0)

    try:
        response = requests.post(
            url,
            files={
                'file': (
                    image_file.name,
                    image_file.read(),
                    'application/octet-stream',
                ),
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise InferenceError(
            f'Inference service unavailable: {exc}'
        ) from exc

    return response.json()
