import os
import json
import yaml
import pickle
import networkx as nx
from tqdm import tqdm

# Import our modular components
try:
    from src.graph.entity_extractor import EntityExtractor
    from src.graph.community_detector import CommunityDetector
except ImportError:
    from entity_extractor import EntityExtractor
    from community_detector import CommunityDetector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

class GraphBuilder:
    def __init__(self):
        self.extractor = EntityExtractor()
        self.detector = CommunityDetector()
        self.graph = nx.Graph()

    def build_graph(self):
        chunks_path = os.path.join(BASE_DIR, config['paths']['output_chunks'])
        if not os.path.exists(chunks_path):
            raise FileNotFoundError("chunks.json missing. Run chunker first.")

        with open(chunks_path, 'r') as f:
            chunks = json.load(f)

        print("Building Knowledge Graph...")
        for chunk in tqdm(chunks):
            chunk_id = f"CHUNK_{chunk['id']}"
            text = chunk['text']
            
            # Add Chunk Node
            self.graph.add_node(chunk_id, type="chunk", text=text)
            
            # Extract & Add Entities
            entities = self.extractor.extract_entities(text)
            for entity in entities:
                self.graph.add_node(entity, type="entity")
                self.graph.add_edge(chunk_id, entity)
                
                # Link Co-occurring Entities 
                for other in entities:
                    if entity != other:
                        if self.graph.has_edge(entity, other):
                            self.graph[entity][other]['weight'] += 1
                        else:
                            self.graph.add_edge(entity, other, weight=1)

        # Save Graph (GML for visual, PKL for app)
        nx.write_gml(self.graph, os.path.join(BASE_DIR, config['paths']['graph_path']))
        
        # REQUIRED: Saving as pickle for the assignment requirements
        pkl_path = os.path.join(BASE_DIR, "processed", "knowledge_graph.pkl")
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.graph, f)
            
        print(f"Graph Built: {self.graph.number_of_nodes()} nodes.")

    def run_community_detection(self):
        print("Running Community Detection...")
        partition = self.detector.detect(self.graph)
        
        # Group nodes by community
        communities = {}
        for node, comm_id in partition.items():
            if comm_id not in communities:
                communities[comm_id] = []
            communities[comm_id].append(node)
            
        out_path = os.path.join(BASE_DIR, config['paths']['community_path'])
        with open(out_path, 'w') as f:
            json.dump(communities, f)
        print(f"Communities saved to {out_path}")

if __name__ == "__main__":
    builder = GraphBuilder()
    builder.build_graph()
    builder.run_community_detection()