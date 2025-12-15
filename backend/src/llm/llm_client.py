import yaml
import os
# NEW IMPORT: Using the dedicated package to avoid warnings
from langchain_ollama import OllamaLLM

# Load Config
# Adjust path logic to find config.yaml regardless of where this script is run
current_dir = os.path.dirname(os.path.abspath(__file__))
# Try to find config in backend root or project root
possible_config_paths = [
    os.path.join(current_dir, "..", "..", "..", "config.yaml"), # If in backend/src/llm
    os.path.join(current_dir, "..", "..", "config.yaml")        # If in src/llm
]

config_path = None
for p in possible_config_paths:
    if os.path.exists(p):
        config_path = p
        break

if not config_path:
    # Fallback default (assuming running from root)
    config_path = "config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

class LLMClient:
    def __init__(self):
        self.model_name = config['llm']['model_name']
        self.temperature = config['llm']['temperature']
        print(f"Initializing Ollama with model: {self.model_name}...")
        
        # NEW CLASS USAGE: OllamaLLM instead of Ollama
        self.llm = OllamaLLM(
            model=self.model_name,
            temperature=self.temperature
        )

    def generate_answer(self, prompt):
        """
        Sends a prompt to the LLM and returns the text response.
        """
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "Sorry, I encountered an error generating the response."