import os
from dotenv import load_dotenv
from agent_system.graph import build_graph

load_dotenv()

def run():
    app = build_graph()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY is not set. Running with mocked LLM nodes to demonstrate the graph flow.")
        from agent_system.tests.test_graph import mock_planner_node, mock_code_writer_node, mock_pr_opener_node
        import agent_system.graph
        agent_system.graph.planner_node = mock_planner_node
        agent_system.graph.code_writer_node = mock_code_writer_node
        agent_system.graph.pr_opener_node = mock_pr_opener_node
        # Rebuild graph with mocked nodes
        app = agent_system.graph.build_graph()
    
    initial_state = {
        "issue": {
            "title": "Fix off-by-one error in loop",
            "body": "The loop in process_data() is skipping the last element.",
            "number": 1,
            "repo": "test/repo"
        },
        "code_context": "def process_data(arr):\n    for i in range(len(arr) - 1):\n        print(arr[i])",
        "retry_count": 0,
        "error_log": []
    }
    
    print("Starting Skateboard Run...")
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Node '{key}' completed.")
            print(f"State Update: {value}")
            print("-" * 40)

if __name__ == "__main__":
    run()
