import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure agent_system is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from agent_system.graph import build_graph
from github import Github
import re

# Create an MCP server
mcp = FastMCP("AgentGraph")

@mcp.tool()
async def resolve_github_issue(issue_url: str) -> str:
    """
    Launch the multi-agent system to resolve a GitHub issue autonomously.
    The agents will search the repository, write code, run tests in Docker, and generate a PR.
    
    Args:
        issue_url: The full GitHub issue URL (e.g., 'https://github.com/Kava-Labs/kava/issues/9999')
    """
    try:
        # Parse URL
        match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", issue_url)
        if not match:
            return "Invalid GitHub Issue URL format."
            
        repo_name = match.group(1)
        issue_number = int(match.group(2))
        
        # Fetch issue details
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            issue_title = issue.title
            issue_body = issue.body or "No description provided."
        else:
            issue_title = f"Resolve issue {issue_number}"
            issue_body = "Please investigate the issue."
        # Build the graph
        graph = build_graph()
        
        initial_state = {
            "issue": {
                "title": issue_title,
                "body": issue_body,
                "number": issue_number,
                "repo": repo_name,
                "url": issue_url
            },
            "code_context": "",
            "retry_count": 0,
            "error_log": []
        }
        
        # In a real environment, you might not want to await the entire graph execution
        # inside the tool call if it takes 5+ minutes, but for demonstration we await it.
        print(f"Starting Multi-Agent Resolution for {repo_name}#{issue_number}...")
        
        final_state = await graph.ainvoke(initial_state)
        
        pr_url = final_state.get("pr_url", "No PR URL generated.")
        
        return f"Successfully resolved issue {issue_number}!\nPull Request opened here: {pr_url}"
        
    except Exception as e:
        return f"Failed to resolve issue: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server in stdio mode
    mcp.run()
