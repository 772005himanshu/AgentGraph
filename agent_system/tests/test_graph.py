import pytest
from agent_system.graph import build_graph
from agent_system.state import AgentState
from agent_system.nodes import planner, code_writer

def mock_planner_node(state: AgentState) -> dict:
    return {
        "plan": "Mock plan to fix the off-by-one error.",
        "complexity": "simple"
    }

def mock_code_writer_node(state: AgentState) -> dict:
    return {
        "patch": "def process_data(arr):\n    for i in range(len(arr)):\n        print(arr[i])"
    }

def mock_pr_opener_node(state: AgentState) -> dict:
    return {
        "pr_url": "https://github.com/mock/repo/pull/1"
    }

def test_graph_execution(monkeypatch):
    # Monkeypatch the nodes in the graph module where they are imported and used
    monkeypatch.setattr("agent_system.graph.planner_node", mock_planner_node)
    monkeypatch.setattr("agent_system.graph.code_writer_node", mock_code_writer_node)
    monkeypatch.setattr("agent_system.graph.pr_opener_node", mock_pr_opener_node)
    
    app = build_graph()
    
    initial_state = {
        "issue": {"title": "Test Issue"},
        "code_context": "Test Context",
        "retry_count": 0,
        "error_log": []
    }
    
    # We can invoke the graph on the initial state
    final_state = app.invoke(initial_state)
    
    # Assertions
    assert final_state["plan"] == "Mock plan to fix the off-by-one error."
    assert final_state["complexity"] == "simple"
    assert "patch" in final_state
    assert final_state["pr_url"] == "https://github.com/mock/repo/pull/1"
