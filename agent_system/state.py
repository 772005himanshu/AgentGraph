from typing import TypedDict, Literal

class AgentState(TypedDict):
    issue: dict              # title, body, number, repo
    code_context: str        # relevant files/snippets pulled by Code Reader
    plan: str                # structured plan from Planner
    complexity: Literal["simple", "complex"]
    patch: str               # diff/patch produced by Code Writer
    tests: str               # test file(s) produced by Test Writer
    test_result: dict        # {"passed": bool, "output": str}
    retry_count: int
    pr_url: str | None
    error_log: list[str]
