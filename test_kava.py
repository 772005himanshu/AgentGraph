import os
import asyncio
from dotenv import load_dotenv
from agent_system.graph import build_graph

load_dotenv()

async def run_kava_test():
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY is missing! The system will fall back to mock mode.")
        print("Please add it to your .env file to run a real test against Kava-Labs/kava.")
    
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️ GITHUB_TOKEN is missing! PyGithub might hit rate limits, or use mock mode.")

    app = build_graph()
    
    # Example issue from Kava-Labs/kava
    initial_state = {
        "issue": {
            "title": "Investigate consensus failure on high load",
            "body": "The node panics during heavy transaction load due to an apparent race condition in the mempool.",
            "number": 9999,
            "repo": "Kava-Labs/kava",
            "url": "https://github.com/Kava-Labs/kava/issues/9999"
        },
        "code_context": "",
        "retry_count": 0,
        "error_log": []
    }
    
    print("\n🚀 Starting Multi-Agent Orchestrator on Kava-Labs/kava...\n")
    
    try:
        # Use astream to print node updates
        async for output in app.astream(initial_state):
            for key, value in output.items():
                print(f"✅ Node [{key.upper()}] completed.")
                if key == "code_reader":
                    print(f"Context Found:\n{str(value.get('code_context'))[:200]}...\n")
                elif key == "planner":
                    print(f"Plan: {value.get('plan')}\nComplexity: {value.get('complexity')}\n")
                elif key == "sandbox":
                    result = value.get('test_result', {})
                    print(f"Sandbox Passed: {result.get('passed')}\nOutput:\n{result.get('output', '')[:100]}\n")
                print("-" * 50)
                
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(run_kava_test())
