import sys
import os
import networkx as nx
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.pipeline.ambedkargpt import AmbedkarGPT

app = FastAPI(title="AmbedkarGPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Booting up AmbedkarGPT Core...")
try:
    bot = AmbedkarGPT()
    print("✅ System Ready!")
except Exception as e:
    print(f"❌ Error initializing system: {e}")
    bot = None

class QueryRequest(BaseModel):
    query: str

def sanitize_results(results):
    """
    CRITICAL FIX: Converts NumPy types (float32) to standard Python types (float)
    so JSON serialization doesn't crash.
    """
    clean_results = []
    for r in results:
        # Create a copy to avoid modifying original data
        item = r.copy()
        if 'score' in item:
            item['score'] = float(item['score']) # Convert numpy.float32 -> float
        if 'embedding' in item:
            del item['embedding'] # Remove heavy embeddings if present
        clean_results.append(item)
    return clean_results

def get_subgraph_for_results(results):
    if not bot: return {"nodes": [], "links": []}
    
    full_graph = bot.local_search.graph
    relevant_nodes = set()
    
    retrieved_text = " ".join([r['text'] for r in results])
    
    for node in full_graph.nodes():
        if node.lower() in retrieved_text.lower():
            relevant_nodes.add(node)
            
    if len(relevant_nodes) > 20:
        relevant_nodes = list(relevant_nodes)[:20]
        
    subgraph = full_graph.subgraph(relevant_nodes)
    return nx.node_link_data(subgraph)

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    if not bot: raise HTTPException(status_code=500, detail="System offline")
    
    query = request.query
    
    # 1. Retrieval
    local_results = bot.local_search.search(query, top_k=5)
    global_results = bot.global_search.search(query, top_k=2)
    reranked_local = bot.ranker.rerank(local_results, query)
    
    # 2. Generation
    final_answer = bot.generator.generate(query, reranked_local[:3], global_results[:2])
    
    # 3. Dynamic Graph
    dynamic_graph = get_subgraph_for_results(reranked_local[:3])
    
    # 4. SANITIZE DATA BEFORE RETURNING (The Fix)
    clean_local = sanitize_results(reranked_local[:3])
    clean_global = sanitize_results(global_results[:2])
    
    top_score = clean_local[0]['score'] if clean_local else 0.0
    
    return {
        "answer": final_answer,
        "metrics": {
            "confidence": float(top_score),
            "source_count": len(clean_local) + len(clean_global),
        },
        "context": {
            "local": clean_local,
            "global": clean_global
        },
        "graph_data": dynamic_graph
    }

@app.get("/graph")
def graph_endpoint():
    if not bot: return {"nodes": [], "links": []}
    G = bot.local_search.graph
    degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)
    top_nodes = [n for n, d in degrees[:300]]
    subgraph = G.subgraph(top_nodes)
    return nx.node_link_data(subgraph)