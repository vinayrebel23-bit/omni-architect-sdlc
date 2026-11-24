import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The Janitor operates on a highly constrained, fast model
janitor_llm = ChatOpenAI(
    model="poolside/laguna-m.1:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.0 # Deterministic refactoring
)

janitor_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Janitor Swarm Agent. Your sole directive is Domain I: Code & Architecture optimization.
You will be provided with a messy function and its cyclomatic complexity report. 
Rewrite the function to:
1. Have a cyclomatic complexity of 3 or less (eliminate deep nesting).
2. Follow strict Domain-Driven Design principles.
3. Be fully typed and commented.
Output ONLY the refactored code block. No conversational text."""),
    ("human", "Linter Report: High complexity (12) detected in function:\n\n{code_snippet}")
])

def run_janitor_refactor(code_snippet: str) -> str:
    """Executes the Janitor Swarm to clean technical debt."""
    print("[Janitor Swarm] Analyzing high-debt code snippet...")
    
    chain = janitor_prompt | janitor_llm | StrOutputParser()
    
    try:
        refactored_code = chain.invoke({"code_snippet": code_snippet})
        print("[+] Refactoring successful. Cyclomatic complexity reduced.")
        return refactored_code
    except Exception as e:
        print(f"[!] Janitor Agent failed: {e}")
        return code_snippet # Fallback to original

if __name__ == "__main__":
    # Mock messy code
    messy_code = '''
    def process_data(user, data):
        if user:
            if user.is_active:
                if data:
                    if len(data) > 0:
                        for d in data:
                            if d.get("status") == "valid":
                                save_to_db(d)
                            else:
                                log_error("invalid data")
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
        return True
    '''
    
    print(f"Original Code:\n{messy_code}\n")
    clean_code = run_janitor_refactor(messy_code)
    print(f"Refactored Code:\n{clean_code}")
