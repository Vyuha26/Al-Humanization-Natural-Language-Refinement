from typing import Literal, Optional
from pydantic import BaseModel, Field

Context = Literal["General Writing", "Professional Communication", "Academic Writing", "Reports and Summaries", "Interview Questions", "Candidate Communication", "Business Documents"]
Tone = Literal["Natural", "Professional", "Conversational", "Polished", "Concise"]

class HumanizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    context: Context = "General Writing"
    tone: Tone = "Natural"
    minimal_rewrite: bool = False
    api_key: Optional[str] = None
    provider: Optional[Literal["gemini", "openai"]] = None
    model: Optional[str] = None

class HumanizeResponse(BaseModel):
    humanized_text: str
    changes_summary: str
    extracted_entities: dict
    meaning_validation: dict
    factuality_validation: dict
    warnings: list[str]
