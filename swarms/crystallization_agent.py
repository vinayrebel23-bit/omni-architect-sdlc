import os
import json
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The Crystallization protocol requires high precision coding
crystallizer_llm = ChatOpenAI(
    model="poolside/laguna-m.1:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.0
)

class CrystallizationResult(BaseModel):
    rust_source: str = Field(description="The complete, highly optimized Rust source code mapping 1:1 with the original logic.")
    mcp_schema: str = Field(description="A strict 5-line JSON Schema defining how other agents should interact with this new binary.")

parser = PydanticOutputParser(pydantic_object=CrystallizationResult)

crystallization_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Omni Architect's Final Stage: The Crystallizer.
You will be provided with a Python/JS module that has reached 100% test coverage and is algorithmically stable.
Your directive is to permanently lock this code by transpiling it to Rust for WASM compilation.
1. Translate the code flawlessly to Rust.
2. Define a Model Context Protocol (MCP) JSON schema so other agents can call this module blindly without needing its source code context.
\n{format_instructions}"""),
    ("human", "Crystallize this stable module:\n\n{source_code}")
])

def run_crystallization(source_code: str) -> dict:
    """Executes the Crystallization Protocol: Transpiling to Rust/WASM."""
    print("[Crystallization Swarm] Initiating Metamorphosis...")
    
    chain = crystallization_prompt | crystallizer_llm | parser
    
    try:
        result = chain.invoke({
            "source_code": source_code,
            "format_instructions": parser.get_format_instructions()
        })
        print("[+] Code successfully crystallized to Rust. Source can now be deleted from context memory.")
        return result.model_dump()
    except Exception as e:
        print(f"[!] Crystallization failed: {e}")
        return {"rust_source": "ERROR", "mcp_schema": "ERROR"}

if __name__ == "__main__":
    # Mock perfect, stable Python function
    perfect_code = '''
    def calculate_fibonacci(n: int) -> int:
        if n <= 0: return 0
        elif n == 1: return 1
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    '''
    
    print(f"Original Stable Code:\n{perfect_code}")
    result = run_crystallization(perfect_code)
    
    print("\n--- Rust Metamorphosis ---")
    print(result.get("rust_source", "Failed"))
    print("\n--- MCP Interface Schema ---")
    print(result.get("mcp_schema", "Failed"))
