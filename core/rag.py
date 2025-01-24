import ollama
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from .embedding import EmbeddingProcessor
from ..models.rag_response_data_models import SummaryResponse, SolutionQuery

class BaseAgent(ABC):
    """Abstract base class for RAG agents"""
    def __init__(self, model_name: str = "qwen2.5:3b"):
        self.client = ollama.Client()
        self.options = ollama.Options(temperature=0.2)
        self.model = model_name
    
    @abstractmethod
    def process(self, *args, **kwargs):
        pass

class SummaryAgent(BaseAgent):
    """Agent for generating log summaries"""
    def __init__(self, model_name: str = "qwen2.5:3b"):
        super().__init__(model_name)
        self.system_prompt = """You are an expert log analyst. Analyze the provided logs and create:
        1. A concise summary of the events
        2. Root cause explanation
        3. Severity assessment"""

    def process(self, logs: List[str]) -> SummaryResponse:
        prompt = f"""Analyze these logs and provide output in JSON format:
        {{
            "summary": ["point 1", "point 2", ...],
            "root_cause_expln": "detailed explanation",
            "severity": "HIGH/MEDIUM/LOW with brief reason"
        }}

        Logs:
        {logs}"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options=self.options
            )
            return SummaryResponse(**eval(response.response))
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")

class SolutionAgent(BaseAgent):
    """Agent for generating solutions based on similar cases"""
    def __init__(self, model_name: str = "qwen2.5:3b"):
        super().__init__(model_name)
        self.system_prompt = """You are an expert troubleshooter. Based on the context and similar cases,
        provide detailed technical solutions."""

    def process(self, query: SolutionQuery, similar_cases: List[str]) -> str:
        prompt = f"""Based on the following information, provide a detailed solution:
        
        Context: {query.context}
        Query: {query.query}
        Additional Info: {query.additional_info}
        
        Similar cases:
        {similar_cases}
        
        Provide a step-by-step solution with technical details and best practices."""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=self.system_prompt,
                options=self.options
            )
            return response.response
        except Exception as e:
            raise Exception(f"Solution generation failed: {str(e)}")

class RAGProcessor:
    """Main RAG processing class"""
    def __init__(
        self,
        collection_name: str,
        embedding_model: str = "nomic-embed-text",
        summary_model: str = "qwen2.5:3b",
        solution_model: str = "qwen2.5:3b"
    ):
        self.embedding_processor = EmbeddingProcessor(
            collection_name=collection_name,
            embedding_model=embedding_model
        )
        self.summary_agent = SummaryAgent(summary_model)
        self.solution_agent = SolutionAgent(solution_model)

    def add_to_knowledge_base(
        self,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add documents to knowledge base"""
        self.embedding_processor.add_documents(texts=texts, metadata=metadata)

    def get_log_summary(self, logs: List[str]) -> SummaryResponse:
        """Generate summary for logs"""
        return self.summary_agent.process(logs)

    def get_solution(
        self,
        query: SolutionQuery,
        n_similar: int = 5
    ) -> str:
        """Get solution based on similar cases"""
        # Get similar cases from vector store
        similar_cases = self.embedding_processor.query_similar(
            query_text=" ".join(query.context),
            n_results=n_similar
        )
        
        # Extract documents from results
        similar_docs = similar_cases.get('documents', [[]])[0]
        
        # Generate solution
        return self.solution_agent.process(query, similar_docs)