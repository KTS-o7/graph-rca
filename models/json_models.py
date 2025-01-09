from pydantic import BaseModel

class GraphNode(BaseModel):
    id: int
    time_stamp: str
    log_level: str
    log_message: str
    log_source: str
    
# Add more data models as required
# this will be directly dumped into Database
