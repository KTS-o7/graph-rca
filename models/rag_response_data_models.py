from pydantic import BaseModel, Field
from typing import  Optional

class SummaryResponse(BaseModel):
    summary: list[str] = Field(description="list of summary points extracted from logs")
    root_cause_expln: str = Field(description="Explanation of the identified root cause")
    severity: str = Field(description="Severity level of the issue")

class SolutionQuery(BaseModel):
    context: str = Field(description="Context information for the query")
    query: str = Field(description="Generated or provided query text")
    response: str = Field(description="Solution response from the LLM")
    sources: list[str] = Field(default=[], description="list of documentation sources used")