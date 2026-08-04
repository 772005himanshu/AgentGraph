import asyncio
import json
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import os
import sys

# Ensure agent_system is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_system.graph import build_graph

app = FastAPI(title="AgentGraph Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for streams (In production, use Redis or DB)
run_streams = {}

from github import Github
import re
from dotenv import load_dotenv

load_dotenv()

class IssueSubmit(BaseModel):
    issue_url: str

@app.post("/api/issues")
async def submit_issue(issue: IssueSubmit):
    # Parse URL
    match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", issue.issue_url)
    if not match:
        return {"error": "Invalid GitHub Issue URL format."}
        
    repo_name = match.group(1)
    issue_number = int(match.group(2))
    
    run_id = f"{repo_name.replace('/', '-')}-{issue_number}"
    
    # Initialize the queue for streaming
    queue = asyncio.Queue()
    run_streams[run_id] = queue
    
    # Start the graph in the background
    asyncio.create_task(run_agent_graph(run_id, issue.issue_url, repo_name, issue_number, queue))
    
    return {"run_id": run_id, "status": "started"}

async def run_agent_graph(run_id: str, issue_url: str, repo_name: str, issue_number: int, queue: asyncio.Queue):
    try:
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

        # Build graph
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
        
        # Async stream
        async for output in graph.astream(initial_state):
            for node_name, state_update in output.items():
                event_data = {
                    "node": node_name,
                    "update": state_update
                }
                await queue.put(json.dumps(event_data))
                
        # Send complete event
        await queue.put("[DONE]")
    except Exception as e:
        await queue.put(json.dumps({"error": str(e)}))
        await queue.put("[DONE]")

@app.get("/api/issues/{run_id}/stream")
async def stream_issue_progress(run_id: str, request: Request):
    queue = run_streams.get(run_id)
    if not queue:
        return {"error": "Run not found"}

    async def event_generator():
        while True:
            # If client disconnects
            if await request.is_disconnected():
                break
                
            data = await queue.get()
            if data == "[DONE]":
                yield {"data": data}
                break
                
            yield {"data": data}
            
    return EventSourceResponse(event_generator())
