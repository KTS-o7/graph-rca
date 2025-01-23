import pytest
from models.context_data_models import Context
from models.graph_data_models import DAG, DAGNode
from models.parsing_data_models import LogEntry, LogChain, SystemInfo, UserInfo, TraceInfo
from models.rag_response_data_models import SummaryResponse, SolutionQuery

# LogEntry Tests
def test_log_entry_with_all_fields():
    log_entry = LogEntry(
        timestamp="2023-01-01 10:00:00",
        message="Test message",
        level="INFO",
        system_info=SystemInfo(pid=1234, component="test-component"),
        user_info=UserInfo(username="test-user", ip_address="127.0.0.1", group="test-group"),
        trace_info=TraceInfo(trace_id="abc-123", request_id="req-123")
    )
    assert log_entry.timestamp == "2023-01-01 10:00:00"
    assert log_entry.system_info.pid == 1234
    assert log_entry.user_info.group == "test-group"
    assert log_entry.trace_info.trace_id == "abc-123"

def test_log_entry_minimal_fields():
    log_entry = LogEntry(
        timestamp="2023-01-01",
        message="test",
        level="INFO",
        system_info=SystemInfo(pid=1234,component=None,error_code=None),
        user_info=UserInfo(username="test",ip_address=None,group=None),
        trace_info=TraceInfo(trace_id=None,request_id="req-123")
    )
    assert log_entry.timestamp == "2023-01-01"
    assert log_entry.system_info is not None
    assert log_entry.user_info is not None
    assert log_entry.trace_info is not None

# SystemInfo Tests
def test_system_info_optional_fields():
    system_info = SystemInfo(pid=1234, component=None, error_code=None)
    assert system_info.pid == 1234
    assert system_info.component is None
    assert system_info.error_code is None

def test_system_info_all_fields():
    system_info = SystemInfo(pid=1234, component="test", error_code=500)
    assert system_info.error_code == 500

# UserInfo Tests
def test_user_info_optional_fields():
    user_info = UserInfo(username="test", ip_address=None, group=None)
    assert user_info.username == "test"
    assert user_info.ip_address is None
    assert user_info.group is None

# TraceInfo Tests
def test_trace_info_optional_fields():
    trace_info = TraceInfo(request_id="req-123", trace_id=None)
    assert trace_info.request_id == "req-123"
    assert trace_info.trace_id is None

# DAG Tests
def test_dag_with_multiple_nodes():
    log_entry1 = LogEntry(timestamp="2023-01-01", message="test1", level="INFO",user_info=None,system_info=None,trace_info=None)
    log_entry2 = LogEntry(timestamp="2023-01-01", message="test2", level="ERROR",user_info=None,system_info=None,trace_info=None)
    
    node1 = DAGNode(id="1", parent_id=None, children=["2"], log_entry=log_entry1)
    node2 = DAGNode(id="2", parent_id="1", children=[], log_entry=log_entry2)
    
    log_chain = LogChain(log_chain=[log_entry1, log_entry2])
    
    dag = DAG(
        nodes=[node1, node2],
        root_id="1",
        root_cause="Test cause",
        leaf_ids=["2"],
        log_chain=log_chain
    )
    assert len(dag.nodes) == 2
    assert dag.leaf_ids == ["2"]

def test_dag_without_root_cause():
    log_entry = LogEntry(timestamp="2023-01-01", message="test", level="INFO",user_info=None,system_info=None,trace_info=None)
    node = DAGNode(id="1", parent_id=None, children=[], log_entry=log_entry)
    log_chain = LogChain(log_chain=[log_entry])
    
    dag = DAG(
            nodes=[node],
            root_id="1",
            root_cause=None,
            leaf_ids=["1"],
            log_chain=log_chain
        )
    assert dag.root_cause is None

# Context Tests
def test_context_with_empty_causal_chain():
    context = Context(
        root_cause="Test cause",
        causal_chain=[]
    )
    assert len(context.causal_chain) == 0

# SummaryResponse Tests
def test_summary_response_with_empty_summary():
    summary = SummaryResponse(
        summary=[],
        root_cause_expln="No issues found",
        severity="Low"
    )
    assert len(summary.summary) == 0

# SolutionQuery Tests
def test_solution_query_with_additional_info():
    query = SolutionQuery(
        context=["Error occurred"],
        query="How to fix?",
        additional_info={"priority": "high"}
    )
    assert query.additional_info["priority"] == "high"

def test_solution_query_without_additional_info():
    query = SolutionQuery(
        context=["Error occurred"],
        query="How to fix?",
        additional_info=None
    )
    assert query.additional_info is None