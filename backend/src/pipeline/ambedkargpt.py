import os
import yaml
import sys

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.retrieval.local_search import LocalSearch
from src.retrieval.global_search import GlobalSearch
from src.retrieval.ranker import Ranker
from src.llm.answer_generator import AnswerGenerator

class AmbedkarGPT:
    def __init__(self):
        print("\n=== Initializing AmbedkarGPT (SemRAG Architecture) ===")
        self.local_search = LocalSearch()
        self.global_search = GlobalSearch()
        self.ranker = Ranker()
        self.generator = AnswerGenerator()
        print("=== System Ready ===\n")

    def query(self, user_query):
        print(f"\nUser Query: {user_query}")
        print("-" * 30)
        
        # 1. Retrieval
        print("1. Retrieving Context...")
        local_results = self.local_search.search(user_query)
        global_results = self.global_search.search(user_query)
        
        # 2. Re-Ranking (The Missing Piece!)
        print("2. Re-Ranking Results...")
        local_results = self.ranker.rerank(local_results, user_query)
        
        # 3. Generation
        print("3. Generating Response...")
        response = self.generator.generate(user_query, local_results[:3], global_results[:2])
        
        print("\n" + "="*30)
        print("FINAL ANSWER")
        print("="*30)
        print(response)
        print("="*30 + "\n")

if __name__ == "__main__":
    bot = AmbedkarGPT()
    while True:
        q = input("Enter your question (or 'exit'): ")
        if q.lower() in ['exit', 'quit']:
            break
        bot.query(q)