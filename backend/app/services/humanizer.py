import json
from typing import Optional
from app.prompts import SYSTEM_PROMPT
from app.services.ai_client import get_ai_client

def _json_object(content: str) -> dict:
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("The AI returned an unreadable response.")
        obj = json.loads(content[start:end+1])
    if not isinstance(obj, dict) or not isinstance(obj.get("humanized_text"), str) or not obj["humanized_text"].strip():
        raise ValueError("The AI response did not contain usable rewritten text.")
    obj.setdefault("changes_summary", "")
    if not isinstance(obj["changes_summary"], str):
        raise ValueError("The AI response contained an invalid changes summary.")
    for key in ("robotic_signals", "uncertain_edits", "warnings"):
        obj.setdefault(key, [])
        if not isinstance(obj[key], list) or any(not isinstance(item, str) for item in obj[key]):
            raise ValueError(f"The AI response contained an invalid {key} list.")
    return obj

def humanize(
    text: str,
    context: str,
    tone: str,
    minimal_rewrite: bool,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model_override: Optional[str] = None
) -> dict:
    client, model = get_ai_client(custom_api_key=api_key, custom_provider=provider, custom_model=model_override)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"original_text": text, "context": context, "tone": tone, "minimal_rewrite": minimal_rewrite}, ensure_ascii=False)}
        ],
    )
    content = response.choices[0].message.content or ""
    return _json_object(content)
