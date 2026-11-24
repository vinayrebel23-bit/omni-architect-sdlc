import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# GrowthOps uses the multimodal reasoning model for UI generation
growthops_llm = ChatOpenAI(
    model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.7 # Higher temperature for creative UI variations
)

growthops_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the GrowthOps / Frontend Swarm Agent.
Your directive is Domain IV: Product & Business optimization.
You will be provided with user conversion drop-off telemetry and a React/HTML component.
1. Generate an A/B test variation of the UI component to improve conversion.
2. Focus on CTA (Call to Action) placement, color psychology, and removing friction.
3. Output ONLY the raw code for 'Variant B'. Do not include markdown formatting or explanations."""),
    ("human", "Telemetry: 45% drop-off at the checkout button on mobile.\nCurrent Component:\n{component_code}")
])

def run_growth_optimization(telemetry: str, component_code: str) -> str:
    """Executes the GrowthOps Swarm to generate UI A/B test variants."""
    print("[GrowthOps Swarm] Analyzing conversion drop-off telemetry...")
    
    chain = growthops_prompt | growthops_llm | StrOutputParser()
    
    try:
        variant_b = chain.invoke({
            "telemetry": telemetry, 
            "component_code": component_code
        })
        print("[+] UI Variant B successfully generated.")
        return variant_b
    except Exception as e:
        print(f"[!] GrowthOps Agent failed: {e}")
        return component_code # Fallback to original UI

if __name__ == "__main__":
    # Mock Growth Data
    mock_telemetry = "Users abandon cart when faced with the small 'Proceed' button."
    mock_ui = '''
    export default function CheckoutButton() {
      return (
        <button style={{ padding: '5px', color: 'gray' }}>
          Proceed
        </button>
      );
    }
    '''
    
    print(f"Original UI (Variant A):\n{mock_ui}")
    new_ui = run_growth_optimization(mock_telemetry, mock_ui)
    print(f"Optimized UI (Variant B):\n{new_ui}")
