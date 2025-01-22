from pydantic import BaseModel, Field
from typing import Optional

"""This module contains Pydantic models for parsing log entries"""

class BaseLogEntry(BaseModel):
    """Base class for all log entries containing common required fields"""
    timestamp: str = Field(description="Timestamp of the log entry")
    message: str = Field(description="Log message content")
    level: str = Field(description="Log level")

class SystemInfo(BaseModel):
    """System-level information"""
    pid: Optional[int] = Field(description="Process ID of the application")
    component: Optional[str] = Field(description="Component/module generating the log")
    error_code: Optional[int] = Field(None, description="Error code if applicable")

class UserInfo(BaseModel):
    """User-related information"""
    username: Optional[str] = Field(description="Username of the user generating the log")
    ip_address: Optional[str] = Field(description="IP address of the user generating the log")
    group: Optional[str] = Field(description="Group of the log entry")

class TraceInfo(BaseModel):
    """Tracing-related information"""
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    request_id: Optional[str] = Field(description="Request ID of the user generating the log")

class LogEntry(BaseLogEntry):
    """Complete log entry combining all information"""
    system_info: Optional[SystemInfo] = Field(default_factory=SystemInfo)
    user_info: Optional[UserInfo] = Field(default_factory=UserInfo)
    trace_info: Optional[TraceInfo] = Field(default_factory=TraceInfo)
    
class LogChain(BaseModel):
    """Collection of log entries"""
    log_chain: list[LogEntry] = Field(description="List of log entries")