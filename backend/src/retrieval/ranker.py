from sentence_transformers import CrossEncoder
import numpy as np

class Ranker:
    def __init__(self):
        # This model is optimized for ranking search results
        # It's small, fast, and runs locally.
        print("Loading Cross-Encoder for Advanced Re-Ranking...")
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, results, query, top_k=5):
        """
        Re-ranks results using a Cross-Encoder model.
        """
        if not results:
            return []

        # Prepare pairs for the model: [[Query, Text1], [Query, Text2], ...]
        passages = [res['text'] for res in results]
        model_inputs = [[query, passage] for passage in passages]
        
        # Predict scores
        scores = self.model.predict(model_inputs)
        
        # Attach scores back to results
        for idx, score in enumerate(scores):
            results[idx]['rerank_score'] = float(score)
            
        # Sort by the new Cross-Encoder score (Descending)
        # We assume cross-encoder score is more accurate than vector score
        ranked_results = sorted(results, key=lambda x: x['rerank_score'], reverse=True)
        
        return ranked_results[:top_k]