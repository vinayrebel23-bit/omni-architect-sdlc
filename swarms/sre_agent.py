import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The SRE requires the massive model to deduce complex root causes
sre_llm = ChatOpenAI(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.0 # Deterministic incident response
)

sre_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the SRE (Site Reliability Engineering) Swarm Agent.
Your directive is to handle Domain II: Quality & Reliability, specifically Incident Response.
You will receive clustered OpenTelemetry/Datadog logs and the last 3 Git commits.
1. Identify the exact commit causing the incident.
2. Determine if a Hotfix (patch) or a Hard Rollback is required.
3. Output a strict JSON plan detailing the mitigation steps.
DO NOT hallucinate. If the blast radius is too large, mandate a hard rollback."""),
    ("human", "Datadog Alert: 500 Error Spike (Rate: 150/sec)\nLogs: {clustered_logs}\nRecent Commits: {recent_commits}")
])

def run_sre_incident_response(clustered_logs: str, recent_commits: str) -> str:
    """Executes the SRE Swarm to mitigate production incidents."""
    print("[SRE Swarm] 🚨 P1 Incident Detected. Analyzing telemetry and commits...")
    
    chain = sre_prompt | sre_llm | StrOutputParser()
    
    try:
        mitigation_plan = chain.invoke({
            "clustered_logs": clustered_logs, 
            "recent_commits": recent_commits
        })
        print("[+] SRE Mitigation Plan Generated.")
        return mitigation_plan
    except Exception as e:
        print(f"[!] SRE Agent failed: {e}")
        return '{"action": "hard_rollback", "reason": "SRE Agent Failure. Defaulting to safe state."}'

if __name__ == "__main__":
    # Mock Incident
    logs = "Error: Cannot read properties of undefined (reading 'userId') at src/api/middleware.js:45"
    commits = "- [a1b2c3d] feat: update auth middleware to use new JWT structure\n- [f4e5d6c] fix: css padding on login"
    
    plan = run_sre_incident_response(logs, commits)
    print(f"\nExecution Plan:\n{plan}")
