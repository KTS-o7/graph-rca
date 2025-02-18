import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest.mock import Mock, patch
from utilz.log_parser import LogParser
from utilz.graph_generator import GraphGenerator
from utilz.context_builder import ContextBuilder
from utilz.database_healthcheck import ServerHealthCheck
from models.parsing_data_models import LogChain, LogEntry, SystemInfo, UserInfo, TraceInfo



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
    def test_parse_valid_log(self, mock_ollama):
        mock_ollama.return_value.generate.return_value = Mock(response=LogEntry(
            timestamp="2023-01-01",
            message="Test message",
            level="INFO",
            system_info=SystemInfo(),
            user_info=UserInfo(),
            trace_info=TraceInfo()
        ))
        
        parser = LogParser()
        result = parser.parse_log("2023-01-01 INFO Test message")
        assert len(result.log_chain) == 1
        assert result.log_chain[0].message == "Test message"

    def test_parse_invalid_file_type(self):
        parser = LogParser()
        with pytest.raises(RuntimeError):
            parser.parse_log_from_file("invalid.csv")

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
