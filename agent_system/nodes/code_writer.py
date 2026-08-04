from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from agent_system.state import AgentState

class CodeWriterOutput(BaseModel):
    patch: str = Field(description="The generated code patch or diff to fix the issue.")

def code_writer_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    structured_llm = llm.with_structured_output(CodeWriterOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software engineer. Write a patch to resolve the issue based on the provided plan."),
        ("user", "Plan: {plan}\nContext: {code_context}\n\nPlease provide the patch.")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "plan": state.get("plan", ""),
        "code_context": state.get("code_context", "")
    })
    
    return {"patch": result.patch}
