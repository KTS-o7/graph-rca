from mirascope.core.groq.call_params import GroqCallParams
from mirascope.core.groq.call_response import GroqCallResponse
from mirascope.core import groq,Messages
from mirascope.core.groq import GroqTool
from ..models.responses import RootCauseAnalysisResponse
from ..models.graphmodels import GraphNode

ROOT_CAUSE_MODEL = "llama3.3"
ROOT_CAUSE_CALL_PARAMS = GroqCallParams(temperature=0.5, max_tokens=500)

class RootCauseAnalyser:
    """
    This class defines the structure of the Root Cause Analyser.
    """ 
    def __init__(self, groq_tool: GroqTool) -> None:
        self.groq_tool = groq_tool
    
    @groq.groq_call(model=ROOT_CAUSE_MODEL, response_model=RootCauseAnalysisResponse, json_mode=True, call_params=ROOT_CAUSE_CALL_PARAMS)
    def analyse(self, logs: list[GraphNode]) -> RootCauseAnalysisResponse:
        return [
            Messages.System("""
            You are a root cause analysis expert. Analyze the provided logs and determine:
            - The primary root cause of the issue
            - Any contributing factors
            Return the analysis in the specified JSON format.
            """),
            Messages.User(f"""
            Analyze these logs for root cause:
            {logs}

            Return analysis in JSON format matching RootCauseAnalysisResponse.
            """)
        ]
 
 # Add more code here to complete the class