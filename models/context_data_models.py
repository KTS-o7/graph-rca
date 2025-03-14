from pydantic import BaseModel, Field
from typing import Optional

"""This module contains Pydantic models for building context from a Directed Acyclic Graph (DAG)"""

class Context(BaseModel):
    """Context information for the log chain"""
    root_cause: str = Field(description="Root cause of the issue")
    causal_chain: list[str] = Field(description="Causal chain of the issue")
    
class Solution(BaseModel):
    response: str = Field(description="Generated solution response text")
    sources: list[str] = Field(default=[], description="List of reference document sources used")
    