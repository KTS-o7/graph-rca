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
    pid: Optional[int] = Field(None, description="Process ID of the application")
    component: Optional[str] = Field(None, description="Component/module generating the log")
    error_code: Optional[int] = Field(None, description="Error code if applicable")

class UserInfo(BaseModel):
    """User-related information"""
    username: Optional[str] = Field(None, description="Username of the user generating the log")
    ip_address: Optional[str] = Field(None, description="IP address of the user generating the log")
    group: Optional[str] = Field(None, description="Group of the log entry")

class TraceInfo(BaseModel):
    """Tracing-related information"""
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    request_id: Optional[str] = Field(None, description="Request ID of the user generating the log")

class LogEntry(BaseModel):
    """Complete log entry combining all information"""
    timestamp: str = Field(description="Timestamp of the log entry")
    message: str = Field(description="Log message content") 
    level: str = Field(description="Log level")
    pid: str = Field("", description="Process ID of the application")
    component: str = Field("", description="Component/module generating the log")
    error_code: str = Field("", description="Error code if applicable")
    username: str = Field("", description="Username of the user generating the log")
    ip_address: str = Field("", description="IP address of the user generating the log")
    group: str = Field("", description="Group of the log entry")
    trace_id: str = Field("", description="Distributed tracing ID")
    request_id: str = Field("", description="Request ID of the user generating the log")

class LogChain(BaseModel):
    """Collection of log entries"""
    log_chain: list[LogEntry] = Field(description="List of log entries")
