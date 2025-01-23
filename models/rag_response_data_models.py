from pydantic import BaseModel,Field
from typing import Optional,Any

class SummaryResponse(BaseModel):
    summary: list[str]= Field(description="A list of strings explaining the summary of the logs that has been passed")
    root_cause_expln: str = Field(description="Root cause of the problem explained")
    severity: str = Field(description="Severity of the issue highlighted in few words")
    
class SolutionQuery(BaseModel):
    context: list[str] = Field(description="Summarized context and premise of the problem")
    query: str = Field(description="A short direct query for further solution generation")
    additional_info: Optional[Any] = Field(description="Any helpful information regarding the problem")