import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# FinOps uses a mid-tier model for Terraform parsing
finops_llm = ChatOpenAI(
    model="poolside/laguna-m.1:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.1 
)

finops_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the FinOps/DevOps Swarm Agent.
Your directive is Domain III: Infrastructure & Operations.
You will be provided with AWS/GCP Billing Telemetry and the current Terraform configuration.
Your goal is to optimize cloud costs without sacrificing performance.
1. Identify over-provisioned instances (e.g., CPU utilization < 20%).
2. Output a patched Terraform (.tf) block that downscales the instance or shifts it to Serverless.
Output ONLY the Terraform HCL code."""),
    ("human", "Billing Alert: EC2 Costs up 15%. \nTelemetry: {telemetry}\nCurrent Terraform:\n{terraform_code}")
])

def run_finops_optimization(telemetry: str, terraform_code: str) -> str:
    """Executes the FinOps Swarm to rewrite IaC for cost optimization."""
    print("[FinOps Swarm] Analyzing billing telemetry and IaC...")
    
    chain = finops_prompt | finops_llm | StrOutputParser()
    
    try:
        optimized_tf = chain.invoke({
            "telemetry": telemetry, 
            "terraform_code": terraform_code
        })
        print("[+] FinOps Optimization successful. Generating IaC PR.")
        return optimized_tf
    except Exception as e:
        print(f"[!] FinOps Agent failed: {e}")
        return terraform_code # Fallback to original infra

if __name__ == "__main__":
    # Mock FinOps Data
    mock_telemetry = "Instance i-12345 (t3.2xlarge) CPU utilization average 12% over 7 days."
    mock_tf = '''
    resource "aws_instance" "web_server" {
        ami           = "ami-0c55b159cbfafe1f0"
        instance_type = "t3.2xlarge"
        tags = {
            Name = "Production-Web"
        }
    }
    '''
    
    print(f"Original Infra:\n{mock_tf}")
    new_tf = run_finops_optimization(mock_telemetry, mock_tf)
    print(f"Optimized Infra:\n{new_tf}")
