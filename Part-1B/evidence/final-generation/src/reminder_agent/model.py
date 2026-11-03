"""Google Gemini SDK transport and local environment configuration."""

import os
from pathlib import Path
from typing import Any

from src.reminder_agent.errors import ModelConfigurationError, ModelServiceError


def _read_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return values
    except OSError:
        raise ModelConfigurationError("Unable to read local .env configuration") from None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        stripped = stripped.removeprefix("export ")
        name, separator, value = stripped.partition("=")
        if not separator:
            continue
        name = name.strip()
        if name not in {"MODEL_API_KEY", "GEMINI_API_KEY", "MODEL_NAME"}:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[name] = value
    return values


def load_model_config() -> tuple[str, str]:
    dotenv_values = _read_dotenv()
    api_key = os.environ.get("MODEL_API_KEY")
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        api_key = dotenv_values.get("MODEL_API_KEY")
    if api_key is None:
        api_key = dotenv_values.get("GEMINI_API_KEY")
    model_name = os.environ.get("MODEL_NAME")
    if model_name is None:
        model_name = dotenv_values.get("MODEL_NAME")
    if not api_key or not model_name:
        missing = [
            name
            for name, value in (
                ("MODEL_API_KEY or GEMINI_API_KEY", api_key),
                ("MODEL_NAME", model_name),
            )
            if not value
        ]
        raise ModelConfigurationError(
            "Missing required model configuration: " + ", ".join(missing)
        )
    return api_key, model_name


def _gemini_client(api_key: str) -> tuple[Any, type[Exception]]:
    try:
        from google import genai
        from google.genai.errors import APIError
    except ImportError:
        raise ModelConfigurationError(
            "Google GenAI SDK is not installed; install requirements.txt"
        ) from None
    try:
        return genai.Client(api_key=api_key), APIError
    except APIError as exc:
        raise ModelServiceError(
            f"Model client initialization failed ({type(exc).__name__})"
        ) from None


def _provider_error_detail(exc: Exception, api_key: str) -> str:
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None)
    detail = f"Model request failed ({type(exc).__name__})"
    if isinstance(code, (int, str)):
        detail += f" with provider code {code}"
    if isinstance(message, str) and message:
        sanitized = message.replace(api_key, "[REDACTED]")
        detail += f": {sanitized[:300]}"
    return detail


def generate_response(system_prompt: str, user_message: str) -> str:
    api_key, model_name = load_model_config()
    client, provider_error = _gemini_client(api_key)
    try:
        from google.genai import types

        response = client.models.generate_content(
            model=model_name,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                max_output_tokens=512,
                response_mime_type="application/json",
            ),
        )
    except provider_error as exc:
        raise ModelServiceError(_provider_error_detail(exc, api_key)) from None

    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        raise ModelServiceError("Model service returned no text content")
    return text
