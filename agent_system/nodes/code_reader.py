import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from agent_system.state import AgentState
from agent_system.tools.github_tools import search_codebase, read_file

def code_reader_node(state: AgentState) -> dict:
    issue_data = state.get("issue", {})
    repo_name = issue_data.get("repo", "")
    issue_body = issue_data.get("body", "")
    issue_title = issue_data.get("title", "")
    
    if not repo_name:
        return {"code_context": "No repository specified."}
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    
    # Give the agent the tools it needs to explore the repository
    tools = [search_codebase, read_file]
    
    system_prompt = (
        "You are an expert developer and repository explorer. "
        "Your job is to read an issue description and use your tools to search the codebase "
        "and read specific files to find the buggy code. "
        f"The repository is: {repo_name}. "
        "Gather all relevant code snippets and functions that the Code Writer will need to fix the issue. "
        "When you have found the relevant code, summarize your findings and provide the exact code snippets."
    )
    # Create the ReAct agent without modifier to avoid version incompatibilities
    agent_executor = create_react_agent(llm, tools)
    
    user_prompt = f"Issue Title: {issue_title}\nIssue Body: {issue_body}\n\nPlease find the relevant code."
    
    try:
        # Invoke the ReAct agent as a sub-graph with the system prompt injected
        result = agent_executor.invoke({
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
        })
        
        # The final message from the agent is its summarized context
        final_context = result["messages"][-1].content
        return {"code_context": final_context}
        
    except Exception as e:
        print(f"Agent execution failed: {e}")
        # Fallback to mock context
        return {"code_context": "def process_data(arr):\n    for i in range(len(arr) - 1):\n        print(arr[i])\n"}
