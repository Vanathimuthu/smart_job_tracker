import importlib
import json

from django.conf import settings


try:
    OpenAI = importlib.import_module("openai").OpenAI
except ImportError:
    OpenAI = None


class AIServiceError(Exception):
    status_code = 502


class AIConfigurationError(AIServiceError):
    status_code = 503


class AIQuotaError(AIServiceError):
    status_code = 429


def get_provider_name():
    provider = getattr(settings, "AI_PROVIDER", "")
    provider = provider.strip().lower()
    if provider:
        return provider
    if getattr(settings, "GROQ_API_KEY", None):
        return "groq"
    if getattr(settings, "GROK_API_KEY", None) or getattr(settings, "XAI_API_KEY", None):
        return "grok"
    return "openai"


def normalize_openai_error(exc):
    code = getattr(exc, "code", None)
    status_code = getattr(exc, "status_code", None)
    message = str(exc)
    provider = get_provider_name().upper()

    if code == "insufficient_quota" or "insufficient_quota" in message or "exceeded your current quota" in message.lower():
        return AIQuotaError(
            f"{provider} API key has insufficient quota. Add billing/credits for this project or use another API key."
        )
    if status_code == 429 or "rate limit" in message.lower() or "too many requests" in message.lower():
        return AIQuotaError(f"{provider} rate limit reached. Wait a minute and try again, or use a higher-limit API key.")
    return None


def get_model_name():
    provider = get_provider_name()
    if provider == "groq":
        return getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
    if provider in {"grok", "xai"}:
        return (
            getattr(settings, "GROK_MODEL", None)
            or getattr(settings, "XAI_MODEL", None)
            or "grok-2-latest"
        )
    return getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")


def get_client():
    if not OpenAI:
        raise AIConfigurationError("OpenAI Python package is not installed. Run pip install -r requirements.txt.")

    provider = get_provider_name()

    if provider == "groq":
        api_key = getattr(settings, "GROQ_API_KEY", None)
        if not api_key:
            raise AIConfigurationError("GROQ_API_KEY is missing. Add it to Django settings and restart the server.")
        return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    if provider in {"grok", "xai"}:
        api_key = getattr(settings, "GROK_API_KEY", None) or getattr(settings, "XAI_API_KEY", None)
        if not api_key:
            raise AIConfigurationError("GROK_API_KEY or XAI_API_KEY is missing. Add it to Django settings and restart the server.")
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise AIConfigurationError("OPENAI_API_KEY is missing. Add it to Django settings and restart the server.")
    return OpenAI(api_key=api_key)


def clean_json_content(content):
    content = (content or "").strip()
    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
    return content


def chat_text(system_prompt, user_prompt, temperature=0.4):
    try:
        completion = get_client().chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return (completion.choices[0].message.content or "").strip()
    except AIServiceError:
        raise
    except Exception as exc:
        normalized_error = normalize_openai_error(exc)
        if normalized_error:
            raise normalized_error from exc
        raise AIServiceError(f"AI request failed: {exc}") from exc


def chat_json(system_prompt, user_prompt, temperature=0.35):
    try:
        completion = get_client().chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        content = clean_json_content(completion.choices[0].message.content)
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIServiceError("AI returned invalid JSON. Please try again.") from exc
    except AIServiceError:
        raise
    except Exception as exc:
        normalized_error = normalize_openai_error(exc)
        if normalized_error:
            raise normalized_error from exc
        raise AIServiceError(f"AI request failed: {exc}") from exc
