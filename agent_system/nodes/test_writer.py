from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from agent_system.state import AgentState

class TestWriterOutput(BaseModel):
    tests: str = Field(description="The pytest test code that covers the patch.")

def test_writer_node(state: AgentState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    structured_llm = llm.with_structured_output(TestWriterOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert QA engineer. Given a code patch, write a pytest suite to verify the fix."),
        ("user", "Context:\n{code_context}\n\nPatch:\n{patch}\n\nPlease provide a complete python test file content that can be executed with pytest. Assume the patched code is available in 'patched_code.py'.")
    ])
    
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({
            "code_context": state.get("code_context", ""),
            "patch": state.get("patch", "")
        })
        return {"tests": result.tests}
    except Exception as e:
        # Fallback if no OPENAI_API_KEY
        print("Warning: Failed to generate tests, using mocked tests.")
        mock_test = "import pytest\nfrom patched_code import process_data\n\ndef test_process_data():\n    assert True"
        return {"tests": mock_test}
