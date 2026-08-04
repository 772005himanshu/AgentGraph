# 🤖 AgentGraph

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-AI-blue?style=for-the-badge)](https://python.langchain.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-8A2BE2?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Sandboxed-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

**AgentGraph** is an autonomous, multi-agent AI framework designed to resolve GitHub issues end-to-end. You provide a GitHub Issue URL, and AgentGraph takes over: it researches the codebase, plans a fix, writes the code, generates tests, verifies everything inside an isolated Docker sandbox, and finally opens a Pull Request.

🟢 **Live Demo:** [https://agentgraph-ui.vercel.app](https://agentgraph-ui.vercel.app)

---

## 🏗 Architecture

The system is built on a modern, decoupled architecture:

1. **Frontend (Next.js)**: A sleek, modern glassmorphism UI. Users can submit GitHub Issue URLs and watch the AI agents work in real-time via Server-Sent Events (SSE). It includes a timeline viewer, a code diff viewer, and real-time terminal logs from the Docker sandbox.
2. **Backend (FastAPI)**: A high-performance asynchronous API that handles frontend requests, streams SSE events back to the client, and orchestrates the heavy lifting of the LangGraph agents.
3. **Agent Graph (LangGraph)**: The core state machine and brain of the application. It routes the AI through specialized "nodes" to methodically solve complex software engineering tasks.
4. **Isolated Sandbox (Docker)**: An ephemeral, highly secure Python container (`network_disabled=True`) that safely executes generated code and tests to ensure the AI's patch actually works before opening a PR.

---

## 🧠 The Agent Workflow

AgentGraph breaks down the complex task of "fixing a bug" into a pipeline of specialized AI agents:

1. 🔍 **Code Reader**: A ReAct agent equipped with codebase search and file reading tools. It dynamically explores the repository to understand the bug's context.
2. 📝 **Planner**: Analyzes the issue and the gathered code context to draft a step-by-step implementation plan.
3. 💻 **Code Writer**: Takes the plan and writes the actual code patch/diff to fix the issue.
4. 🧪 **Test Writer**: Generates a comprehensive `pytest` suite to verify that the Code Writer's patch actually resolves the bug.
5. 🐳 **Docker Sandbox**: Spins up a secure container, applies the patch, and runs the tests. If tests fail, it feeds the error logs back into the graph for self-correction.
6. 🚀 **PR Opener**: Once the sandbox tests pass, it uses the GitHub API to create a new branch, commit the changes, and open a Pull Request.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (v3.11+)
- **Docker** Desktop/Daemon running on your host machine
- **API Keys**: Google Gemini API Key (`GOOGLE_API_KEY`) and optionally a GitHub PAT (`GITHUB_TOKEN`).

### 2. Environment Setup

Clone the repository and set up your environment variables. Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token # Optional
```

### 3. Start the Backend (FastAPI)

Open a terminal window and run:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies (assuming a requirements.txt exists, or use uv/pip)
pip install -r requirements.txt # or install fastapi uvicorn langchain-google-genai etc.

# Start the FastAPI server on port 8000
uvicorn backend.main:app --reload --port 8000
```

### 4. Start the Frontend (Next.js)

Open a **second** terminal window and run:

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` in your browser. Paste a GitHub issue URL into the search bar, click **Resolve**, and watch the agents go to work!

---

## 🔌 MCP Server Integration

AgentGraph also natively acts as a Model Context Protocol (MCP) Server! This means you can expose the entire orchestration engine as a tool (`resolve_github_issue`) to external IDEs like **Cursor** or **Windsurf**.

To run it as an MCP server:
```bash
npx @modelcontextprotocol/inspector uv run backend/mcp_server.py
```

---

## 🔒 Security & Trust Boundaries

- **Zero Host Execution**: Generated test code is **never** executed on your host machine. All execution happens in an ephemeral Docker container with network access completely disabled.
- **Branch-Only Writes**: The agent is hardcoded to never push directly to `main` or `master`. It exclusively creates side branches and opens Pull Requests for human review.

---
*Built with Next.js, FastAPI, LangGraph, Model Context Protocol (MCP), and Google Gemini.*
