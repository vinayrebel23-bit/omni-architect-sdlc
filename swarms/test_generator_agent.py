import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The Test Generator uses a fast coding model
tester_llm = ChatOpenAI(
    model="cohere/north-mini-code:free", # Specifically selected for fast coding scripts
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.1
)

tester_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Test Verification Swarm Agent.
Your directive is Phase 2: Forging the Shield.
You will receive a piece of source code. Your job is to write a comprehensive unit test suite (using Jest for JS, or PyTest for Python).
1. Ensure you test the "Happy Path".
2. Ensure you test at least 2 edge cases or failure modes (e.g., null inputs, extreme values).
3. Output ONLY the raw test code. Do not include conversational text."""),
    ("human", "Generate a test suite for the following code:\n\n{source_code}")
])

def run_test_generation(source_code: str) -> str:
    """Executes the Test Generator Swarm to build the safety net."""
    print("[Test Swarm] Generating comprehensive unit tests...")
    
    chain = tester_prompt | tester_llm | StrOutputParser()
    
    try:
        test_suite = chain.invoke({"source_code": source_code})
        print("[+] Test Suite generated successfully.")
        return test_suite
    except Exception as e:
        print(f"[!] Test Agent failed: {e}")
        return "" # Return empty if failed

if __name__ == "__main__":
    # Mock source code
    mock_code = '''
    def divide(a, b):
        return a / b
    '''
    
    print(f"Source Code:\n{mock_code}")
    tests = run_test_generation(mock_code)
    print(f"Generated Tests:\n{tests}")
