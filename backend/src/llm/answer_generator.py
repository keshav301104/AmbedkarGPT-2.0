from .llm_client import LLMClient
from .prompt_templates import PromptTemplates

class AnswerGenerator:
    def __init__(self):
        self.llm = LLMClient()
        self.prompts = PromptTemplates()

    def generate(self, query, local_context, global_context):
        # Format Context with IDs for Citation
        full_context = ""
        citation_map = []
        
        counter = 1
        
        # Add Local Context (Specifics)
        full_context += "--- SPECIFIC EVIDENCE ---\n"
        for item in local_context:
            snippet = item['text'].replace('\n', ' ')
            full_context += f"[{counter}] {snippet}\n"
            citation_map.append(f"[{counter}] Source: {item.get('source', 'Local Search')}")
            counter += 1
            
        # Add Global Context (Themes)
        full_context += "\n--- BROAD THEMES ---\n"
        for item in global_context:
            snippet = item['text'].replace('\n', ' ')
            full_context += f"[{counter}] {snippet}\n"
            citation_map.append(f"[{counter}] Source: {item.get('source', 'Global Search')}")
            counter += 1

        # Prepare Prompt
        prompt = self.prompts.get_answer_prompt(full_context, query)
        
        # Generate Answer
        print("   -> Sending prompt to LLM...")
        raw_answer = self.llm.generate_answer(prompt)
        
        # Append Source Key to the bottom for the user to see
        final_output = f"{raw_answer}\n\n--- Sources ---\n" + "\n".join(citation_map)
        
        return final_output