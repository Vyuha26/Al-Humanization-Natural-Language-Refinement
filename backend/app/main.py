import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import HumanizeRequest
from app.services.humanizer import humanize
from app.services.validator import validate
from app.services.document_extractor import extract_document, MAX_TEXT_CHARS
from app.utils.entity_checks import extract_entities, compare_entities

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="HumanizeAI API", version="1.0.0")
origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin, "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValueError)
async def value_error(_, exc): return __import__("fastapi").responses.JSONResponse(status_code=422, content={"detail":str(exc)})

@app.get("/")
def root():
    has_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return {"name": "HumanizeAI API", "status": "ok", "ai_configured": has_key}

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/api/extract-document")
async def extract(file: UploadFile = File(...)):
    data = await file.read(5 * 1024 * 1024 + 1)
    try: return extract_document(file.filename or "upload", data)
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/humanize")
def process(req: HumanizeRequest):
    text = req.text.strip()
    if not text: raise HTTPException(status_code=422, detail="Enter some text before humanizing.")
    if len(text) > MAX_TEXT_CHARS: raise HTTPException(status_code=413, detail="Text is limited to 20,000 characters.")
    try:
        result = humanize(text, req.context, req.tone, req.minimal_rewrite, api_key=req.api_key, provider=req.provider, model_override=req.model)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        from openai import APITimeoutError, AuthenticationError, RateLimitError
        if isinstance(e, (TimeoutError, APITimeoutError)):
            raise HTTPException(status_code=504, detail="The AI request timed out. Please try again.")
        if isinstance(e, AuthenticationError):
            raise HTTPException(status_code=401, detail="Invalid AI API Key. Please check your API key.")
        if isinstance(e, RateLimitError):
            err_msg = str(e)
            if "insufficient_quota" in err_msg or "credit_balance_exhausted" in err_msg or "credits" in err_msg.lower():
                raise HTTPException(status_code=429, detail="AI credit balance exhausted or quota reached. Please add credits to your account or provide an alternative API key.")
            raise HTTPException(status_code=429, detail="AI request rate limit reached. Please wait a moment and try again.")
        raise HTTPException(status_code=502, detail="Humanization could not be completed. Please check your API key configuration and try again.")
    warnings = list(result.get("warnings", [])) + compare_entities(text, result["humanized_text"])
    result["extracted_entities"] = extract_entities(text)
    try:
        validation = validate(text, result["humanized_text"], api_key=req.api_key, provider=req.provider, model_override=req.model)
        meaning = {k:validation[k] for k in ("meaning_status","meaning_explanation","changed_facts","added_claims","omitted_claims","review_warnings")}
        factuality = {k:validation[k] for k in ("factuality_status","factuality_explanation","changed_facts","added_claims","omitted_claims","review_warnings")}
        warnings.extend(validation.get("review_warnings", []))
    except Exception:
        meaning = {"meaning_status":"Review recommended","meaning_explanation":"Independent validation was unavailable. Review the rewrite against your original.","changed_facts":[],"added_claims":[],"omitted_claims":[],"review_warnings":[]}
        factuality = {"factuality_status":"Review recommended","factuality_explanation":"Automated factual consistency validation was unavailable; factual correctness is not guaranteed.","changed_facts":[],"added_claims":[],"omitted_claims":[],"review_warnings":[]}
        warnings.append("Independent validation could not run. Review important details yourself.")
    if warnings:
        if meaning["meaning_status"] == "Passed": meaning["meaning_status"] = "Review recommended"
        if factuality["factuality_status"] == "Passed": factuality["factuality_status"] = "Review recommended"
    warnings.append("Automated checks can miss errors and do not verify claims against external sources. Review important content.")
    return {"humanized_text":result["humanized_text"],"changes_summary":result.get("changes_summary",""),"extracted_entities":result["extracted_entities"],"meaning_validation":meaning,"factuality_validation":factuality,"warnings":list(dict.fromkeys(warnings))}

@app.post("/api/humanize-document")
async def humanize_document(file: UploadFile = File(...), context: str = "General Writing", tone: str = "Natural", minimal_rewrite: bool = False):
    # Reuse the same extraction and processing pipeline after enforcing option values via the request schema.
    from app.schemas import HumanizeRequest
    data = await file.read(5 * 1024 * 1024 + 1)
    try: extracted = extract_document(file.filename or "upload", data)
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))
    try: opts = HumanizeRequest(text=extracted["extracted_text"], context=context, tone=tone, minimal_rewrite=minimal_rewrite)
    except Exception as e: raise HTTPException(status_code=422, detail="Unsupported writing context or tone.") from e
    return {"extraction":extracted,"result":process(opts)}
