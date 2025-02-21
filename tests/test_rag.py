import pytest
from unittest.mock import Mock, patch, MagicMock
from core.rag import RAG_Engine
from models.rag_response_data_models import SummaryResponse, SolutionQuery
from langchain.schema import Document
import ollama
import json

@pytest.fixture
def mock_ollama():
    with patch('ollama.Client') as mock:
        yield mock

@pytest.fixture
def rag_engine(mock_ollama):
    return RAG_Engine()

@pytest.fixture
def sample_docs():
    return ["Doc 1 content", "Doc 2 content", "Doc 3 content"]

class TestRAGEngine:
    def test_generate_summary_success(self, rag_engine, mock_ollama):
        # Mock Ollama response
        mock_response = {
            'response': "Summary line 1\nSummary line 2",
            'status_code': 200
        }
        rag_engine.ollama_client.generate = Mock(return_value=mock_response)
        
        context = ["Error log 1", "Warning log 2"]
        result = rag_engine.generate_summary(context)
        
        assert isinstance(result, SummaryResponse)
        assert len(result.summary) == 2
        assert result.root_cause_expln == "Identified via log analysis"
        assert result.severity == "High"
        rag_engine.ollama_client.generate.assert_called_once_with(
            model="llama3.2:3b",
            prompt=f"Summarize this log context and identify root cause:\n{'\n'.join(context)}",
            options={"temperature": 0.2}
        )

    def test_generate_solution_success(self, rag_engine):
        # Setup mocks
        mock_doc = Document(
            page_content="Sample doc text",
            metadata={"source": "kb123"}
        )
        rag_engine.vector_db.search = Mock(return_value=[mock_doc])
        rag_engine.ollama_client.generate = Mock(return_value={
            'response': "Detailed solution steps...",
            'status_code': 200
        })
        
        result = rag_engine.generate_solution("error context", "root cause")
        
        assert isinstance(result, SolutionQuery)
        assert "Detailed solution steps" in result.response
        assert "kb123" in result.sources
        assert result.query.startswith("Provide resolution steps for:")

    def test_generate_solution_vector_search_error(self, rag_engine, capsys):
        rag_engine.vector_db.search = Mock(side_effect=Exception("DB error"))
        error_doc = Document(
            page_content="Error searching documentation",
            metadata={"source": "error"}
        )
        rag_engine.vector_db.search = Mock(return_value=[error_doc])
        rag_engine.ollama_client.generate = Mock(return_value={'response': "..."})
        
        result = rag_engine.generate_solution("context", "root cause")
        
        assert "..." in result.response

    def test_generate_solution_llm_failure(self, rag_engine):
        valid_doc = Document(page_content="valid doc")
        rag_engine.vector_db.search = Mock(return_value=[valid_doc])
        rag_engine.ollama_client.generate = Mock(side_effect=Exception("LLM down"))
        
        result = rag_engine.generate_solution("context", "root cause")
        
        assert "Error: Unable to generate solution from LLM" in result.response
        assert result.sources == ['Unknown']

    def test_store_documentation_success(self, rag_engine, sample_docs):
        # Mock dependencies
        rag_engine.embedder.create_batch_embeddings = Mock(return_value=[[0.1]*768]*3)
        rag_engine.vector_db.add_documents = Mock()
        rag_engine.vector_db.get_collection = Mock(return_value=MagicMock(count=Mock(return_value=3)))
        
        rag_engine.store_documentation(sample_docs)
        
        rag_engine.vector_db.add_documents.assert_called_once()
        assert rag_engine.embedder.create_batch_embeddings.call_count == 1

    def test_store_documentation_empty_input(self, rag_engine):
        with pytest.raises(ValueError):
            rag_engine.store_documentation([])

    def test_generate_solution_context_conversion(self, rag_engine):
        # Test different context types
        test_cases = [
            (["list", "context"], "list\ncontext"),
            (("tuple", "context"), "tuple\ncontext"),
            (123, "123"),
            ({"key": "value"}, str({"key": "value"}))
        ]
        
        for context_input, expected_output in test_cases:
            rag_engine.vector_db.search = Mock(return_value=[])
            rag_engine.ollama_client.generate = Mock(return_value={'response': ''})
            
            result = rag_engine.generate_solution(context_input, "cause")
            assert result.context == expected_output

    def test_generate_solution_malformed_llm_response(self, rag_engine):
        valid_doc = Document(page_content="valid doc")
        rag_engine.vector_db.search = Mock(return_value=[valid_doc])
        rag_engine.ollama_client.generate = Mock(return_value={})  # Empty response
        
        result = rag_engine.generate_solution("context", "root cause")
        
        assert "No response received from LLM" in result.response

    def test_store_documentation_chunk_validation(self, rag_engine):
        rag_engine.embedder.create_batch_embeddings = Mock(return_value=[])
        with pytest.raises(ValueError):
            rag_engine.store_documentation(["valid", "docs"])
