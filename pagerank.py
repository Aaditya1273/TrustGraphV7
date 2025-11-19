#!/usr/bin/env python3
"""PageRank Analysis - Compute reputation scores from Trust Atoms"""

from src.algorithms.pagerank import TrustPageRank
from src.data.guardian_processor import GuardianProcessor
from src.core.stake_validator import StakeValidator


def main():
    print("📊 Trust Graph v7 - PageRank Analysis\n")
    
    stake_validator = StakeValidator()
    processor = GuardianProcessor(stake_validator)
    pagerank = TrustPageRank(damping_factor=0.85, iterations=30)
    
    # Generate mock Guardian dataset
    print("🔄 Generating mock Guardian social graph...")
    guardian_data = processor.generate_mock_guardian_data(50)
    print(f"  Nodes: {len(guardian_data['nodes'])}")
    print(f"  Edges: {len(guardian_data['edges'])}\n")
    
    # Register stakes for some nodes
    print("💰 Registering stakes...")
    for i, node in enumerate(guardian_data["nodes"][:20]):
        stake = 50 + i * 100
        stake_validator.register_stake(node["did"], stake)
    print(f"  Registered 20 stakers\n")
    
    # Convert to Trust Atoms
    print("⚙️  Converting edges to Trust Atoms...")
    atoms = processor.process_dataset(guardian_data)
    print(f"  Generated {len(atoms)} Trust Atoms\n")
    
    # Build PageRank graph
    print("🕸️  Building trust network graph...")
    for atom in atoms:
        stake_weight = stake_validator.calculate_stake_weight(atom.issuer)
        pagerank.add_trust_atom(atom, stake_weight)
    print("  Graph built\n")
    
    # Compute PageRank
    print("🧮 Computing weighted PageRank...")
    top_nodes = pagerank.get_top_n(15)
    
    print("\n🏆 Top 15 Most Trusted Nodes:\n")
    for i, entry in enumerate(top_nodes, 1):
        node_id = entry["node"][:24]
        score = entry["score"] * 100
        bar = "█" * int(entry["score"] * 30)
        print(f"{i:2d}. {node_id}... {bar} {score:.2f}%")
    
    print("\n📈 Network Statistics:")
    stats = pagerank.get_stats()
    print(f"  Total Nodes: {stats['nodeCount']}")
    print(f"  Total Edges: {stats['edgeCount']}")
    print(f"  Avg Score: {stats['avgScore'] * 100:.2f}%")
    print(f"  Max Score: {stats['maxScore'] * 100:.2f}%")
    print(f"  Min Score: {stats['minScore'] * 100:.2f}%")
    
    print("\n💎 Stake Statistics:")
    print(stake_validator.get_stats())
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
