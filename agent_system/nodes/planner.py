from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Literal
from agent_system.state import AgentState

class PlannerOutput(BaseModel):
    plan: str = Field(description="Step by step plan to fix the issue")
    complexity: Literal["simple", "complex"] = Field(description="Complexity of the issue")

def planner_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    structured_llm = llm.with_structured_output(PlannerOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software architect. Given a GitHub issue and code context, devise a plan to fix it."),
        ("user", "Issue: {issue}\n\nContext: {code_context}")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({
        "issue": state.get("issue", {}),
        "code_context": state.get("code_context", "No context provided.")
    })
    
    return {
        "plan": result.plan,
        "complexity": result.complexity
    }
