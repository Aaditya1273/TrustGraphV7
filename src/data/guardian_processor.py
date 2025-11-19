"""Guardian Dataset Processor - Converts social graph to Trust Atoms"""

import random
from typing import List, Dict
from ..core.trust_atom import TrustAtomV7, TrustVector
from ..core.stake_validator import StakeValidator


class GuardianProcessor:
    """Process Umanitek Guardian social graph data"""
    
    def __init__(self, stake_validator: StakeValidator):
        self.stake_validator = stake_validator
        self.processed_count = 0
    
    def generate_mock_guardian_data(self, node_count: int = 100) -> Dict:
        """Generate mock Guardian dataset"""
        nodes = []
        edges = []
        
        # Generate nodes
        for i in range(node_count):
            nodes.append({
                "id": f"user_{i}",
                "did": f"did:guardian:{self._random_hash(16)}",
                "platform": random.choice(["Twitter", "Reddit", "TikTok", "YouTube"]),
                "followers": random.randint(0, 10000),
                "verified": random.random() > 0.7,
                "content_quality": random.random()
            })
        
        # Generate edges
        for _ in range(node_count * 3):
            from_node = random.choice(nodes)
            to_node = random.choice(nodes)
            
            if from_node["id"] != to_node["id"]:
                edges.append({
                    "from": from_node["did"],
                    "to": to_node["did"],
                    "type": random.choice(["follow", "endorse"]),
                    "weight": random.random(),
                    "from_node": from_node,
                    "to_node": to_node
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def edge_to_trust_atom(self, edge: Dict) -> TrustAtomV7:
        """Convert edge to Trust Atom"""
        from_node = edge.get("from_node", {})
        to_node = edge.get("to_node", {})
        
        # Calculate trust vector based on node properties
        base_honesty = 0.8 if to_node.get("verified") else 0.6
        base_expertise = to_node.get("content_quality", 0.5) * 0.9 + 0.1
        
        trust_vector = TrustVector(
            honesty=min(1.0, base_honesty + random.random() * 0.15),
            expertise=min(1.0, base_expertise + random.random() * 0.1),
            bias=min(1.0, 0.3 + random.random() * 0.3),
            safety=min(1.0, 0.7 + random.random() * 0.25),
            speed=min(1.0, 0.6 + random.random() * 0.3),
            alignment=min(1.0, 0.65 + random.random() * 0.25),
            responsiveness=min(1.0, 0.7 + random.random() * 0.2),
            stake_weight=self.stake_validator.calculate_stake_weight(edge["from"])
        )
        
        content = (
            f"Endorsed for quality content on {to_node.get('platform', 'platform')}"
            if edge["type"] == "endorse"
            else f"Trusted connection on {to_node.get('platform', 'platform')}"
        )
        
        atom = TrustAtomV7(
            issuer=edge["from"],
            target=edge["to"],
            trust_vector=trust_vector,
            content=content,
            evidence_ka=[f"guardian:edge:{self._random_hash(8)}"],
            required_stake="100" if trust_vector.honesty > 0.7 else "0"
        )
        
        return atom
    
    def process_dataset(self, guardian_data: Dict) -> List[TrustAtomV7]:
        """Convert Guardian dataset to Trust Atoms"""
        atoms = []
        
        for edge in guardian_data["edges"]:
            atom = self.edge_to_trust_atom(edge)
            atoms.append(atom)
            self.processed_count += 1
        
        print(f"✓ Processed {self.processed_count} Guardian edges into Trust Atoms")
        return atoms
    
    @staticmethod
    def _random_hash(length: int) -> str:
        """Generate random hex hash"""
        chars = "abcdef0123456789"
        return "".join(random.choice(chars) for _ in range(length))
