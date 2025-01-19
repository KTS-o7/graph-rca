from pydantic import BaseModel,Field


"""
    This file will contain pydantic models for Node of the DAG for logs.
    Each node will have a a unique ID, a list of parents, level of logging, log message, timestamp.
"""

class GraphNode(BaseModel):
    """
    This class defines the structure of a node in the DAG.
    """
    id: str = Field(...,description="Unique ID of the node")
    parents: list = Field(...,description="List of parent nodes")
    level: str = Field(...,description="Level of logging")
    log: str = Field(...,description="Log message")
    timestamp: str = Field(...,description="Timestamp of the log")
    
# add more models here