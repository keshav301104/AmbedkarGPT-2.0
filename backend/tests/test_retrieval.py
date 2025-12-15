import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.ranker import Ranker

class TestRetrieval(unittest.TestCase):
    def setUp(self):
        # We assume Ranker is initialized. 
        # If Ranker loads a model, this might take a second.
        self.ranker = Ranker()
        self.sample_results = [
            {"text": "Caste is a social evil.", "score": 0.5, "id": 1},
            {"text": "Democracy is essential for liberty.", "score": 0.4, "id": 2}
        ]

    def test_reranking_logic(self):
        """Test if the ranker functionality returns a list"""
        query = "social evil"
        # We mock the prediction to avoid downloading models during quick tests
        # In a real test, you'd run the actual model
        try:
            reranked = self.ranker.rerank(self.sample_results, query)
            self.assertIsInstance(reranked, list)
            self.assertEqual(len(reranked), 2)
        except Exception as e:
            self.fail(f"Ranker crashed: {e}")

if __name__ == '__main__':
    unittest.main()