from agent_system.state import AgentState

def pr_opener_node(state: AgentState) -> dict:
    # In Phase 1, we just mock the PR Opener
    print("Mocking PR Opener...")
    print(f"Creating PR for patch:\n{state.get('patch')}")
    
    return {"pr_url": "https://github.com/mock/repo/pull/1"}
