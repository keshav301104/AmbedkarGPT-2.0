import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class BufferMerger:
    def __init__(self, threshold=0.6, max_tokens=1024):
        self.threshold = threshold
        self.max_tokens = max_tokens

    def should_merge(self, current_chunk_emb, next_sent_emb, current_tokens, next_tokens):
        """
        Decides if the next sentence should be merged into the current buffer.
        """
        # 1. Check Token Limit
        if (current_tokens + next_tokens) >= self.max_tokens:
            return False
            
        # 2. Check Semantic Similarity
        # FIX: Use len() check. This is safe for both Python Lists and NumPy Arrays.
        if len(current_chunk_emb) == 0:
            return True
            
        # Compare NEW sentence against the AVERAGE embedding of the current chunk
        current_mean = np.mean(current_chunk_emb, axis=0).reshape(1, -1)
        next_sent = next_sent_emb.reshape(1, -1)
        
        similarity = cosine_similarity(current_mean, next_sent)[0][0]
        
        return similarity >= self.threshold