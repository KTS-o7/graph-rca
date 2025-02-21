import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest.mock import Mock, patch
from utilz.log_parser import LogParser
from utilz.graph_generator import GraphGenerator
from utilz.context_builder import ContextBuilder
from utilz.database_healthcheck import ServerHealthCheck
from utilz.database_healthcheck import check_services
from models.parsing_data_models import LogChain, LogEntry, SystemInfo, UserInfo, TraceInfo
from pathlib import Path
import json



# Test LogParser
@pytest.fixture
def mock_ollama():
    with patch('ollama.Client') as mock:
        yield mock

@pytest.fixture
def sample_log_chain():
    return LogChain(log_chain=[
        LogEntry(
            timestamp="2023-01-01",
            message="Error occurred",
            level="ERROR",
            system_info=SystemInfo(),
            user_info=UserInfo(),
            trace_info=TraceInfo()
        ),
        LogEntry(
            timestamp="2023-01-02",
            message="System recovery",
            level="INFO",
            system_info=SystemInfo(),
            user_info=UserInfo(),
            trace_info=TraceInfo()
        )
    ])

class TestLogParser:
    @pytest.fixture
    def mock_ollama(self):
        with patch('ollama.Client') as mock:
            yield mock

    def test_parse_valid_log(self, mock_ollama):
        # Create a proper mock response object
        mock_response = Mock()
        mock_response.response = json.dumps({
            "timestamp": "2023-01-01",
            "message": "Test message",
            "level": "INFO",
            "pid": "1234",
            "component": "",
            "error_code": "",
            "username": "",
            "ip_address": "",
            "group": "",
            "trace_id": "",
            "request_id": ""
        })
        
        mock_ollama.return_value.generate.return_value = mock_response
        
        parser = LogParser()
        result = parser.parse_log("2023-01-01 INFO Test message")
        assert len(result.log_chain) == 1
        assert result.log_chain[0].message == "Test message"

    def test_parse_invalid_file_type(self, tmp_path):
        parser = LogParser()
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.touch()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_log_from_file(str(invalid_file))
        assert "Unsupported file type" in str(exc_info.value)

    def test_empty_log_data(self):
        parser = LogParser()
        with pytest.raises(RuntimeError):
            parser.parse_log("")

# Test GraphGenerator
class TestGraphGenerator:
    def test_dag_generation(self, sample_log_chain):
        generator = GraphGenerator(sample_log_chain)
        dag = generator.generate_dag()
        
        assert len(dag.nodes) == 2
        assert dag.root_id is not None
        assert len(dag.leaf_ids) == 1

    def test_parent_child_relationships(self, sample_log_chain):
        generator = GraphGenerator(sample_log_chain)
        dag = generator.generate_dag()
        
        parent = next(n for n in dag.nodes if n.id == dag.root_id)
        assert len(parent.children) == 1

    def test_single_node_graph(self):
        log_chain = LogChain(log_chain=[
            LogEntry(
                timestamp="2023-01-01",
                message="Single entry",
                level="INFO",
                system_info=SystemInfo(),
                user_info=UserInfo(),
                trace_info=TraceInfo()
            )
        ])
        generator = GraphGenerator(log_chain)
        dag = generator.generate_dag()
        
        assert dag.root_id == dag.leaf_ids[0]

# Test ContextBuilder
class TestContextBuilder:
    def test_valid_context_creation(self, sample_log_chain):
        generator = GraphGenerator(sample_log_chain)
        dag = generator.generate_dag()
        
        builder = ContextBuilder()
        context = builder.build_context(dag)
        
        assert len(context.causal_chain) == 2
        assert "Error occurred" in context.causal_chain

    def test_empty_dag_handling(self):
        builder = ContextBuilder()
        with pytest.raises(RuntimeError):
            builder.build_context(None)

# Test DatabaseHealthCheck
@pytest.fixture
def mock_chroma():
    with patch('chromadb.HttpClient') as mock:
        instance = mock.return_value
        instance.heartbeat.return_value = True
        yield mock

@pytest.fixture
def mock_pymongo():
    with patch('pymongo.MongoClient') as mock:
        instance = mock.return_value
        instance.server_info.return_value = {'ok': 1.0}
        yield mock

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.columns') as mock_cols:
        with patch('streamlit.success') as mock_success:
            with patch('streamlit.error') as mock_error:
                # Create mock column objects that support context manager
                col1 = Mock()
                col2 = Mock()
                # Add context manager methods
                col1.__enter__ = Mock(return_value=col1)
                col1.__exit__ = Mock(return_value=None)
                col2.__enter__ = Mock(return_value=col2)
                col2.__exit__ = Mock(return_value=None)
                # Make columns return the list of column objects
                mock_cols.return_value = [col1, col2]
                yield {
                    'columns': mock_cols,
                    'success': mock_success,
                    'error': mock_error,
                    'col1': col1,
                    'col2': col2
                }

class TestDatabaseHealthCheck:
    def test_chroma_connection_success(self, mock_chroma):
        checker = ServerHealthCheck()
        assert checker.check_chroma() is True

    def test_mongo_connection_success(self, mock_pymongo):
        checker = ServerHealthCheck()
        assert checker.check_mongo() is True

    def test_chroma_connection_failure(self, mock_chroma):
        mock_chroma.return_value.heartbeat.side_effect = Exception("Connection failed")
        checker = ServerHealthCheck()
        assert "Connection failed" in str(checker.check_chroma())

    def test_mongo_connection_failure(self, mock_pymongo):
        mock_pymongo.return_value.server_info.side_effect = Exception("Auth failed")
        checker = ServerHealthCheck()
        assert "Auth failed" in str(checker.check_mongo())

    def test_chroma_returns_zero(self, mock_chroma):
        mock_chroma.return_value.heartbeat.return_value = 0
        checker = ServerHealthCheck()
        assert checker.check_chroma() is False

    def test_mongo_returns_invalid_ok(self, mock_pymongo):
        mock_pymongo.return_value.server_info.return_value = {'ok': 0.0}
        checker = ServerHealthCheck()
        assert checker.check_mongo() is False

    def test_check_services_all_success(self, mock_chroma, mock_pymongo, mock_streamlit):
        check_services()
        
        # Verify success messages were displayed
        mock_streamlit['success'].assert_any_call("ChromaDB Connected")
        mock_streamlit['success'].assert_any_call("MongoDB Connected")
        assert mock_streamlit['error'].call_count == 0

    def test_check_services_all_failure(self, mock_chroma, mock_pymongo, mock_streamlit):
        # Make both connections fail
        mock_chroma.return_value.heartbeat.side_effect = Exception("Chroma failed")
        mock_pymongo.return_value.server_info.side_effect = Exception("Mongo failed")
        
        check_services()
        
        # Verify error messages were displayed
        mock_streamlit['error'].assert_any_call("ChromaDB Connection Failed")
        mock_streamlit['error'].assert_any_call("MongoDB Connection Failed")
        assert mock_streamlit['success'].call_count == 0

    def test_check_services_mixed_results(self, mock_chroma, mock_pymongo, mock_streamlit):
        # Make Chroma succeed but Mongo fail
        mock_chroma.return_value.heartbeat.return_value = 1
        mock_pymongo.return_value.server_info.side_effect = Exception("Mongo failed")
        
        check_services()
        
        # Verify appropriate messages were displayed
        mock_streamlit['success'].assert_called_once_with("ChromaDB Connected")
        mock_streamlit['error'].assert_called_once_with("MongoDB Connection Failed")
