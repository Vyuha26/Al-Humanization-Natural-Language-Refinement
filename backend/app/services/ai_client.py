import os
from typing import Optional, Tuple
from openai import OpenAI

def _normalize_gemini_model(model_name: Optional[str]) -> str:
    valid_env = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    if not model_name or model_name in ("gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"):
        return valid_env
    return model_name

def get_ai_client(
    custom_api_key: Optional[str] = None,
    custom_provider: Optional[str] = None,
    custom_model: Optional[str] = None
) -> Tuple[OpenAI, str]:
    """
    Returns an OpenAI client instance configured for Google Gemini or OpenAI,
    along with the model identifier to use.
    """
    env_gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    env_openai_key = os.getenv("OPENAI_API_KEY")

    if custom_api_key:
        is_gemini = custom_provider == "gemini" or (not custom_provider and (custom_api_key.startswith("AIza") or custom_api_key.startswith("AQ.") or "gemini" in (custom_model or "").lower()))
        if is_gemini:
            model = _normalize_gemini_model(custom_model)
            return OpenAI(
                api_key=custom_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=45,
                max_retries=1
            ), model
        else:
            model = custom_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
            return OpenAI(
                api_key=custom_api_key,
                timeout=45,
                max_retries=1
            ), model

    # Env-based selection: prioritize Gemini if set
    if env_gemini_key:
        model = _normalize_gemini_model(custom_model)
        return OpenAI(
            api_key=env_gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=45,
            max_retries=1
        ), model

    if env_openai_key:
        model = custom_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        return OpenAI(
            api_key=env_openai_key,
            timeout=45,
            max_retries=1
        ), model

    raise RuntimeError("AI service is not configured. Add GEMINI_API_KEY or OPENAI_API_KEY to backend/.env and restart the server.")
