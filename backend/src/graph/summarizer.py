import json
import os
import yaml
from tqdm import tqdm
# Import the LLM Client we just made
from src.llm.llm_client import LLMClient

# Load Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

class CommunitySummarizer:
    def __init__(self):
        self.llm_client = LLMClient()

    def load_data(self):
        # Load Communities
        comm_path = os.path.join(BASE_DIR, config['paths']['community_path'])
        with open(comm_path, 'r') as f:
            self.communities = json.load(f)

        # Load Chunks (to get the actual text content)
        chunks_path = os.path.join(BASE_DIR, config['paths']['output_chunks'])
        with open(chunks_path, 'r') as f:
            self.chunks_data = {f"CHUNK_{c['id']}": c['text'] for c in json.load(f)}

    def generate_summaries(self):
        self.load_data()
        summaries = {}
        
        print(f"Generating summaries for {len(self.communities)} communities...")
        print("Note: This relies on your Local LLM, so it might take a few minutes.")

        for comm_id, nodes in tqdm(self.communities.items()):
            # 1. Collect text from this community
            # We look for nodes that are Chunks (start with "CHUNK_")
            texts = [self.chunks_data[node] for node in nodes if node in self.chunks_data]
            
            # If no chunks in this community (only entities), skip or handle gracefully
            if not texts:
                continue
                
            # Limit context to avoid overflowing the LLM (take top 3 chunks)
            combined_text = "\n".join(texts[:3])
            
            # 2. Create Prompt
            prompt = f"""
            You are an expert researcher. Read the following text segments derived from Dr. Ambedkar's book.
            Identify the central theme and write a concise summary (2-3 sentences) explaining what this group of text discusses.
            
            TEXT:
            {combined_text}
            
            SUMMARY:
            """
            
            # 3. Call LLM
            summary = self.llm_client.generate_answer(prompt)
            summaries[comm_id] = summary.strip()

        # Save Summaries
        output_path = os.path.join(BASE_DIR, "processed", "community_summaries.json")
        with open(output_path, 'w') as f:
            json.dump(summaries, f)
        
        print(f"Saved community summaries to {output_path}")

if __name__ == "__main__":
    summarizer = CommunitySummarizer()
    summarizer.generate_summaries()