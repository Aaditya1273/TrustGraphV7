"""Weighted PageRank for Trust Networks"""

import networkx as nx
from typing import List, Dict, Tuple
from ..core.trust_atom import TrustAtomV7


class TrustPageRank:
    """Compute reputation scores using weighted PageRank"""
    
    def __init__(self, damping_factor: float = 0.85, iterations: int = 20):
        self.damping_factor = damping_factor
        self.iterations = iterations
        self.graph = nx.DiGraph()
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0):
        """Add weighted edge to graph"""
        self.graph.add_edge(from_node, to_node, weight=weight)
    
    def add_trust_atom(self, atom: TrustAtomV7, stake_weight: float = 1.0):
        """Add Trust Atom as weighted edge"""
        edge_weight = atom.overall * stake_weight
        self.add_edge(atom.issuer, atom.target, edge_weight)
    
    def compute(self) -> Dict[str, float]:
        """Compute PageRank scores"""
        if len(self.graph.nodes()) == 0:
            return {}
        
        # Use NetworkX's pagerank with edge weights
        scores = nx.pagerank(
            self.graph,
            alpha=self.damping_factor,
            max_iter=self.iterations,
            weight='weight'
        )
        
        # Normalize to 0-1 range
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {node: score / max_score for node, score in scores.items()}
        
        return scores
    
    def get_ranked_nodes(self) -> List[Tuple[str, float]]:
        """Get nodes ranked by score"""
        scores = self.compute()
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    def get_top_n(self, n: int = 10) -> List[Dict]:
        """Get top N nodes"""
        ranked = self.get_ranked_nodes()
        return [{"node": node, "score": score} for node, score in ranked[:n]]
    
    def get_stats(self) -> Dict:
        """Get network statistics"""
        scores = self.compute()
        values = list(scores.values())
        
        return {
            "nodeCount": len(self.graph.nodes()),
            "edgeCount": len(self.graph.edges()),
            "avgScore": sum(values) / len(values) if values else 0,
            "maxScore": max(values) if values else 0,
            "minScore": min(values) if values else 0
        }
