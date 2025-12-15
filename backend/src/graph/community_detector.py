import community.community_louvain as community_louvain

class CommunityDetector:
    def detect(self, graph):
        """
        Detects communities in a NetworkX graph using Louvain algorithm.
        Returns: {node: community_id}
        """
        # Louvain is standard for SemRAG community detection [cite: 2243]
        try:
            partition = community_louvain.best_partition(graph)
            return partition
        except Exception as e:
            print(f"Community Detection Error: {e}")
            return {}