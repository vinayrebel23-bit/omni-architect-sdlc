import os
import json
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# SecOps Gate uses the Safety model to scan code
secops_llm = ChatOpenAI(
    model="nvidia/nemotron-3.5-content-safety:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.0
)

# Define the strict output for the Security Gate
class SecurityScanResult(BaseModel):
    is_safe: bool = Field(description="True if the code contains ZERO vulnerabilities. False if any risk is detected.")
    vulnerability_type: str = Field(description="If unsafe, list the OWASP Top 10 category (e.g., 'SQL Injection', 'XSS'). Otherwise, 'None'.")
    explanation: str = Field(description="Brief technical explanation of the security risk or confirmation of safety.")

parser = PydanticOutputParser(pydantic_object=SecurityScanResult)

secops_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the SecOps Gate Swarm Agent.
Your directive is Phase 2: Forging the Shield.
You will receive a Git PR Diff containing code changes.
Scan the code for OWASP Top 10 vulnerabilities (SQLi, XSS, Hardcoded Secrets, Command Injection).
Output your findings strictly matching the requested JSON schema.
\n{format_instructions}"""),
    ("human", "Scan this PR Diff for security vulnerabilities:\n\n{pr_diff}")
])

def run_secops_gate(pr_diff: str) -> dict:
    """Executes the SecOps Gate to scan PRs before merging."""
    print("[SecOps Gate] Scanning PR Diff for vulnerabilities...")
    
    chain = secops_prompt | secops_llm | parser
    
    try:
        scan_result = chain.invoke({
            "pr_diff": pr_diff,
            "format_instructions": parser.get_format_instructions()
        })
        print(f"[+] Security Scan Complete. Is Safe? {scan_result.is_safe}")
        return scan_result.model_dump()
    except Exception as e:
        print(f"[!] SecOps Agent failed: {e}")
        # Fail Secure: If the scanner breaks, the code is deemed UNSAFE
        return {"is_safe": False, "vulnerability_type": "Scanner Failure", "explanation": "Security scanner failed to parse. Code blocked."}

if __name__ == "__main__":
    # Mock PR Diff with a glaring SQL Injection
    mock_diff = '''
    + def get_user(user_id):
    +     query = f"SELECT * FROM users WHERE id = {user_id}"
    +     db.execute(query)
    '''
    
    print("Scanning mock diff with SQL Injection...")
    result = run_secops_gate(mock_diff)
    print(json.dumps(result, indent=2))
