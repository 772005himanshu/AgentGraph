# AgentGraph: Multi-Agent GitHub Issue Resolver

A fullstack application that takes a GitHub Issue and autonomously researches the codebase, drafts a fix, writes tests, runs them in an isolated Docker sandbox, and opens a pull request.

## Architecture

1. **Frontend (Next.js)**: A stunning glassmorphism dashboard that allows users to submit issues and watch the agents work in real-time via Server-Sent Events (SSE).
2. **Backend (FastAPI)**: Serves the SSE endpoints and orchestrates the background agent execution.
3. **MCP Server**: Exposes the entire orchestrator as a tool (`resolve_github_issue`) for external AI IDEs (Cursor, Windsurf) or Claude Desktop using the `mcp` Python SDK.
4. **Agent Graph (LangGraph)**: The core state machine routing the AI through nodes (`Code Reader` -> `Planner` -> `Code Writer` -> `Test Writer` -> `Docker Sandbox` -> `PR Opener`).
   - *Note: The Code Reader is a true ReAct agent equipped with `search_codebase` and `read_file` tools to dynamically explore the repository.*
5. **Sandbox (Docker)**: An ephemeral, completely isolated Python container with zero network access and restricted CPU/Memory that executes the generated pytest suite against the generated code patch.

## How to Run

### 1. Prerequisites
- Docker daemon running on your machine.
- Node.js installed (for the frontend).
- Python 3.11+ installed (using `uv` is recommended).
- An Google Gemini API Key (`GOOGLE_API_KEY`).
- A GitHub Personal Access Token (`GITHUB_TOKEN`) - optional, falls back to mock data.

### 2. Setup the Environment
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your-key-here
GITHUB_TOKEN=your-github-token # optional
```

### 3. Start the Web Backend (FastAPI)
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

### 4. Start the Web Frontend (Next.js)
```bash
cd frontend
npm run dev
```
Visit `http://localhost:3000` in your browser.

### 5. Running as an MCP Server
You can connect your MCP Client (like the Inspector) directly to the MCP Server:
```bash
npx @modelcontextprotocol/inspector uv run backend/mcp_server.py
```
This will allow you to call `resolve_github_issue` directly from any compatible AI!

## Trust Boundaries & Security
- **Sandboxing**: Generated test code is NEVER executed on the host machine. It runs in an ephemeral docker container with `network_disabled=True`.
- **Branch-only writes**: The agent is hardcoded to never push to `main` or `master`. It only creates side branches and Pull Requests.
