import os
import json
import yaml
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

class GlobalSearch:
    def __init__(self):
        print("Initializing Global Search Engine...")
        self.model = SentenceTransformer(config['chunking']['model_name'])
        
        # Load Community Summaries
        comm_path = os.path.join(BASE_DIR, "processed", "community_summaries.json")
        
        if not os.path.exists(comm_path):
            raise FileNotFoundError("Community summaries not found! Run summarizer.py first.")
            
        with open(comm_path, 'r') as f:
            self.summaries = json.load(f)
            
        # Prepare Data for Search
        self.comm_ids = list(self.summaries.keys())
        self.comm_texts = list(self.summaries.values())
        
        print(f"Encoding {len(self.comm_texts)} community summaries...")
        self.comm_embeddings = self.model.encode(self.comm_texts)

    def search(self, query, top_k=3):
        """
        Implements SemRAG Equation 5:
        Search against community summaries to find broad contexts.
        """
        if not self.comm_embeddings.any():
            return []

        # 1. Embed Query
        query_emb = self.model.encode([query])
        
        # 2. Calculate Similarity
        sim_scores = cosine_similarity(query_emb, self.comm_embeddings)[0]
        
        # 3. Sort Results
        results = []
        for idx, score in enumerate(sim_scores):
            results.append({
                "text": self.comm_texts[idx],
                "score": score,
                "source": f"Community {self.comm_ids[idx]} Summary"
            })
            
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]

if __name__ == "__main__":
    gs = GlobalSearch()
    results = gs.search("What are the major social themes?")
    for res in results:
        print(f"\n[Score: {res['score']:.2f}] {res['text']}")