from pydantic import BaseModel, Field

"""
    This will contain pydantic models for the response of LLMs.
"""

class RootCauseAnalysisResponse(BaseModel):
    """
    This class defines the structure of the response of the Root Cause Analysis API.
    """ 
    
    root_cause: str = Field(...,description="Root cause of the issue")
    reason_for_root_cause: list[str] = Field(...,description="Reason for the root cause")
    confidence: float = Field(...,description="Confidence of the root cause")
    
# add more models here
