import os
from typing import TypedDict, Annotated, Sequence
import operator
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from orchestrator.parser import sanitize_ticket_content
from orchestrator.semantic_cache import check_cache, store_cache
from orchestrator.graph_memory import graph_db

from swarms.janitor_agent import run_janitor_refactor
from swarms.sre_agent import run_sre_incident_response
from swarms.finops_agent import run_finops_optimization
from swarms.growthops_agent import run_growth_optimization

# --- Configuration for OpenRouter (Free Tier Models) ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The Omni Architect (Meta-Controller)
omni_architect = ChatOpenAI(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.1
)

# The Execution Agent
execution_agent = ChatOpenAI(
    model="poolside/laguna-m.1:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.2
)

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_intent: str
    current_phase: str
    assigned_swarm: str
    swarm_payload: dict
    ci_status: str

# --- Node Functions ---
def sanitize_input_node(state: AgentState):
    """Air-Gapped Parser: Extracts only technical requirements"""
    print(">> Executing Air-Gapped Sanitization...")
    raw_input = state["messages"][-1].content
    sanitized_data = sanitize_ticket_content(raw_input)
    
    if sanitized_data.get("is_malicious_or_injection"):
        print("[!] Security Alert: Malicious intent detected. Halting execution.")
        return {"current_phase": "halted"}
        
    print(f"[+] Task Sanitized: {sanitized_data['technical_objective']}")
    return {"current_phase": "planning", "task_intent": sanitized_data["technical_objective"]}

def architecture_planning_node(state: AgentState):
    """The Omni Architect breaks down the task, queries GraphRAG, and dynamically routes to a Swarm."""
    print(">> Omni Architect: Planning & Querying GraphRAG...")
    task_intent = state.get("task_intent", "").lower()
    
    # 1. Check Semantic Cache
    cached_plan = check_cache(f"plan_{task_intent}")
    if cached_plan:
        print("[+] Used Cached Execution Plan!")
        return {"current_phase": "coding", "assigned_swarm": "general"}
        
    # 2. Dynamic Semantic Routing Matrix
    assigned_swarm = "general"
    payload = {"data": task_intent}
    
    if "refactor" in task_intent or "complexity" in task_intent:
        assigned_swarm = "janitor"
    elif "500 error" in task_intent or "incident" in task_intent:
        assigned_swarm = "sre"
    elif "cost" in task_intent or "aws" in task_intent or "terraform" in task_intent:
        assigned_swarm = "finops"
    elif "conversion" in task_intent or "drop-off" in task_intent:
        assigned_swarm = "growthops"
        
    print(f"[Router] Target Intent detected. Routing to: {assigned_swarm.upper()} SWARM")
    
    return {"current_phase": "coding", "assigned_swarm": assigned_swarm, "swarm_payload": payload}

def execution_node(state: AgentState):
    """Executes the Dynamically Assigned Swarm"""
    swarm = state.get("assigned_swarm", "general")
    print(f">> Executing Swarm Protocol: {swarm.upper()}")
    
    payload = state.get("swarm_payload", {}).get("data", "")
    
    if swarm == "janitor":
        run_janitor_refactor(payload)
    elif swarm == "sre":
        run_sre_incident_response(payload, "recent_commits_mock")
    elif swarm == "finops":
        run_finops_optimization(payload, "terraform_mock")
    elif swarm == "growthops":
        run_growth_optimization(payload, "ui_component_mock")
    else:
        print(f"[General Coder] Executing standard development tasks for: {payload}")
        
    return {"current_phase": "verification"}

def verification_node(state: AgentState):
    """Checks CI/CD status (Woodpecker CI)"""
    print(">> Verification: Waiting for Woodpecker CI...")
    # Mocking CI pass
    return {"ci_status": "pass"}

# --- Edge Routing ---
def route_after_sanitize(state: AgentState):
    """Halts the graph if the input was malicious."""
    if state.get("current_phase") == "halted":
        return "end"
    return "plan"

def route_after_verification(state: AgentState):
    """Decides if we merge or route back to execution (Max 3 retries logic here)"""
    if state.get("ci_status") == "pass":
        return "merge"
    return "execute"

# --- Graph Construction ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("sanitize", sanitize_input_node)
workflow.add_node("plan", architecture_planning_node)
workflow.add_node("execute", execution_node)
workflow.add_node("verify", verification_node)

# Add Edges
workflow.set_entry_point("sanitize")
workflow.add_conditional_edges(
    "sanitize",
    route_after_sanitize,
    {
        "plan": "plan",
        "end": END
    }
)
workflow.add_edge("plan", "execute")
workflow.add_edge("execute", "verify")
workflow.add_conditional_edges(
    "verify",
    route_after_verification,
    {
        "execute": "execute", # Loop back to fix code
        "merge": END # Merge the PR and finish
    }
)

# Compile the State Machine
app = workflow.compile()

if __name__ == "__main__":
    print("Starting Omni Architect SDLC Orchestrator...")
    # Example trigger event
    initial_state = {
        "messages": [HumanMessage(content="Fix the mobile login bug")],
        "task_intent": "Fix mobile login",
        "current_phase": "init",
        "ci_status": "pending"
    }
    
    # Run the graph
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished node: {key}")
            print(f"Current Phase: {value.get('current_phase', 'N/A')}")
            print("---")
