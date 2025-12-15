import os
import json
import yaml
import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

class LocalSearch:
    def __init__(self):
        print("Initializing Local Search Engine...")
        # Load Embedding Model
        self.model = SentenceTransformer(config['chunking']['model_name'])
        
        # Load Graph
        graph_path = os.path.join(BASE_DIR, config['paths']['graph_path'])
        print(f"Loading Graph from {graph_path}...")
        self.graph = nx.read_gml(graph_path)
        
        # Load Chunks (for text content)
        chunks_path = os.path.join(BASE_DIR, config['paths']['output_chunks'])
        with open(chunks_path, 'r') as f:
            self.chunks_map = {f"CHUNK_{c['id']}": c for c in json.load(f)}

        # Cache Entity Embeddings to speed up search
        self.entity_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'entity']
        print(f"Caching embeddings for {len(self.entity_nodes)} entities...")
        self.entity_embeddings = self.model.encode(self.entity_nodes)

    def search(self, query, top_k=5, threshold=0.3):
        """
        Implements Equation 4: Local Search
        1. Embed Query
        2. Find similar Entities (sim(v, Q) > threshold)
        3. Retrieve Chunks linked to those Entities
        """
        # 1. Embed Query
        query_emb = self.model.encode([query])
        
        # 2. Calculate Similarity with all Entities
        sim_scores = cosine_similarity(query_emb, self.entity_embeddings)[0]
        
        # Filter entities by threshold
        relevant_entities = []
        for idx, score in enumerate(sim_scores):
            if score > threshold:
                relevant_entities.append((self.entity_nodes[idx], score))
        
        # Sort by score
        relevant_entities = sorted(relevant_entities, key=lambda x: x[1], reverse=True)
        
        # 3. Find Linked Chunks
        # The equation says: Retrieve chunks (g) connected to relevant entities (v)
        retrieved_chunks = {}
        
        for entity, score in relevant_entities[:10]: # Check top 10 entities
            # Get neighbors in the graph
            neighbors = self.graph.neighbors(entity)
            for neighbor in neighbors:
                # We only want neighbors that are CHUNKS
                if neighbor.startswith("CHUNK_"):
                    if neighbor not in retrieved_chunks:
                        retrieved_chunks[neighbor] = {
                            "text": self.chunks_map[neighbor]['text'],
                            "score": score,  # Inherit score from the entity
                            "source_entity": entity
                        }
                    else:
                        # If chunk already found via another entity, boost score slightly
                        retrieved_chunks[neighbor]['score'] += 0.1

        # Convert to list and sort
        results = list(retrieved_chunks.values())
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]

if __name__ == "__main__":
    # Test it immediately
    searcher = LocalSearch()
    results = searcher.search("What is the origin of Caste?")
    
    print("\n--- Search Results ---")
    for res in results:
        print(f"[Score: {res['score']:.2f}] (Source: {res['source_entity']})")
        print(res['text'][:200] + "...\n")