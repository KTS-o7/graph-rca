from pydantic import BaseModel, Field
from typing import Optional
from .parsing_data_models import LogEntry,LogChain
from uuid import uuid4

"""This module contains Pydantic models to build a Directed Acyclic Graph (DAG) out of parsed log entries"""

class DAGNode(BaseModel):
    """Node in the Directed Acyclic Graph (DAG)"""
    id: str = Field(description="Unique identifier of the node")
    parent_id: Optional[str] = Field(description="Unique identifier of the parent node")
    children: list[str] = Field(description="List of unique identifiers of the children nodes")
    log_entry: LogEntry = Field(description="Log entry information")
    
class DAG(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    """Directed Acyclic Graph (DAG) of log entries"""
    nodes: list[DAGNode] = Field(description="List of nodes in the graph")
    root_id: str = Field(description="Unique identifier of the root node")
    root_cause: Optional[str] = Field(description="Root cause of the issue")
    leaf_ids: list[str] = Field(description="List of unique identifiers of the leaf nodes")
    log_chain: LogChain = Field(description="Collection of log entries")