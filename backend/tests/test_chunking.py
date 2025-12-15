import unittest
from src.chunking.buffer_merger import BufferMerger
import numpy as np

class TestChunking(unittest.TestCase):
    def test_buffer_merger_logic(self):
        merger = BufferMerger(threshold=0.5)
        # Fake embeddings (identical vectors = sim 1.0)
        emb1 = np.array([[1, 0, 0]])
        emb2 = np.array([1, 0, 0])

        should_merge = merger.should_merge(emb1, emb2, 10, 10)
        self.assertTrue(should_merge)

if __name__ == '__main__':
    unittest.main()