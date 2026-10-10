import json
from typing import Optional
from app.prompts import VALIDATOR_PROMPT
from app.services.ai_client import get_ai_client

def validate(
    original: str,
    rewritten: str,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model_override: Optional[str] = None
) -> dict:
    client, model = get_ai_client(custom_api_key=api_key, custom_provider=provider, custom_model=model_override)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": VALIDATOR_PROMPT},
            {"role": "user", "content": json.dumps({"original_text": original, "rewritten_text": rewritten}, ensure_ascii=False)}
        ]
    )
    result = json.loads(response.choices[0].message.content or "{}")
    if not isinstance(result, dict):
        raise ValueError("Validator response was not a JSON object.")
    allowed = {"Passed", "Review recommended", "Potential issue detected"}
    if result.get("meaning_status") not in allowed or result.get("factuality_status") not in allowed:
        raise ValueError("Validator returned an invalid status.")
    for key in ("meaning_explanation", "factuality_explanation"):
        if not isinstance(result.get(key), str):
            raise ValueError(f"Validator returned an invalid {key}.")
    for key in ("changed_facts", "added_claims", "omitted_claims", "review_warnings"):
        result.setdefault(key, [])
        if not isinstance(result[key], list) or any(not isinstance(item, str) for item in result[key]):
            raise ValueError(f"Validator returned an invalid {key} list.")
    return result
