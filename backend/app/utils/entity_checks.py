import re

NUMBER_RE = re.compile(r"(?<!\w)(?:[$€£₹]\s*)?\d[\d,]*(?:\.\d+)?%?(?!\w)")
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b", re.I)

def extract_entities(text: str) -> dict:
    numbers = list(dict.fromkeys(NUMBER_RE.findall(text)))
    dates = list(dict.fromkeys(DATE_RE.findall(text)))
    # Keep this deterministic and modest: capitalized spans are entity candidates, not verified names.
    names = list(dict.fromkeys(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", text)))
    return {"names_and_capitalized_terms": names, "numbers": numbers, "dates": dates}

def compare_entities(original: str, rewritten: str) -> list[str]:
    a, b = extract_entities(original), extract_entities(rewritten)
    warnings = []
    for key, label in [("numbers", "numbers or amounts"), ("dates", "dates"), ("names_and_capitalized_terms", "names or capitalized terms")]:
        missing = [item for item in a[key] if item not in b[key]]
        if missing:
            warnings.append(f"Review {label} that may not have been preserved: {', '.join(missing)}")
    return warnings
