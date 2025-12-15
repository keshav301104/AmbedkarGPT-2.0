import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestIntegration(unittest.TestCase):
    def test_file_structure(self):
        """
        Sanity Check: Do the critical data files exist?
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        files_to_check = [
            os.path.join(base_dir, "processed", "chunks.json"),
            os.path.join(base_dir, "processed", "knowledge_graph.pkl"),
            os.path.join(base_dir, "config.yaml")
        ]
        
        for f_path in files_to_check:
            self.assertTrue(os.path.exists(f_path), f"Missing critical file: {f_path}")

if __name__ == '__main__':
    unittest.main()