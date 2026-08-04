from langgraph.graph import StateGraph, START, END
from agent_system.state import AgentState
from agent_system.nodes.code_reader import code_reader_node
from agent_system.nodes.planner import planner_node
from agent_system.nodes.code_writer import code_writer_node
from agent_system.nodes.test_writer import test_writer_node
from agent_system.nodes.pr_opener import pr_opener_node
from agent_system.sandbox.docker_runner import run_tests_in_sandbox

MAX_RETRIES = 3

def sandbox_node(state: AgentState) -> dict:
    patch = state.get("patch", "")
    tests = state.get("tests", "")
    
    print("Running sandbox...")
    result = run_tests_in_sandbox(patch, tests)
    
    current_log = state.get("error_log", [])
    if not result["passed"]:
        current_log.append(result["output"])
        
    return {
        "test_result": result,
        "error_log": current_log,
        "retry_count": state.get("retry_count", 0) + 1
    }

def route_after_planner(state: AgentState):
    if state.get("complexity") == "complex":
        # In a full implementation, this might route back to code_reader for more research
        # For now, we'll just send it to code_writer
        return "code_writer"
    return "code_writer"

def route_after_sandbox(state: AgentState):
    passed = state.get("test_result", {}).get("passed", False)
    retries = state.get("retry_count", 0)
    
    if passed:
        return "pr_opener"
    
    if retries >= MAX_RETRIES:
        return END # Halt if we exhausted retries and still failing
        
    return "code_writer" # Retry

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("code_reader", code_reader_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("code_writer", code_writer_node)
    workflow.add_node("test_writer", test_writer_node)
    workflow.add_node("sandbox", sandbox_node)
    workflow.add_node("pr_opener", pr_opener_node)
    
    # Connect
    workflow.add_edge(START, "code_reader")
    workflow.add_edge("code_reader", "planner")
    
    workflow.add_conditional_edges("planner", route_after_planner)
    
    workflow.add_edge("code_writer", "test_writer")
    workflow.add_edge("test_writer", "sandbox")
    
    workflow.add_conditional_edges("sandbox", route_after_sandbox)
    
    workflow.add_edge("pr_opener", END)
    
    return workflow.compile()
