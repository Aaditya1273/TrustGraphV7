#!/usr/bin/env python3
"""
Grok Plugin Demo - AI refuses to cite low-honesty sources
This demonstrates how AI agents use Trust Graph v7 for source verification
"""

import requests
import os

MCP_BASE_URL = os.getenv("MCP_URL", "http://localhost:3000")


class GrokTrustFilter:
    """Simulates Grok using Trust Graph MCP to filter sources"""
    
    def __init__(self, min_honesty=0.8):
        self.min_honesty = min_honesty
        self.mcp_url = MCP_BASE_URL
    
    def check_source_trustworthy(self, source_id):
        """Check if source meets minimum honesty threshold"""
        try:
            response = requests.post(
                f"{self.mcp_url}/mcp/check_trust_threshold",
                json={
                    "target": source_id,
                    "dimension": "honesty",
                    "threshold": self.min_honesty
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["meetsThreshold"], result["score"]
            
            return False, 0.0
            
        except Exception as e:
            print(f"⚠️  Error checking source: {e}")
            return False, 0.0
    
    def generate_response_with_citation(self, query, potential_sources):
        """Generate response, only citing trustworthy sources"""
        print(f"\n🤖 Grok Query: {query}\n")
        
        verified_sources = []
        rejected_sources = []
        
        for source in potential_sources:
            is_trustworthy, honesty_score = self.check_source_trustworthy(source["id"])
            
            if is_trustworthy:
                verified_sources.append({
                    **source,
                    "honesty": honesty_score
                })
                print(f"✅ {source['name']}: Honesty {honesty_score:.2%} - APPROVED")
            else:
                rejected_sources.append({
                    **source,
                    "honesty": honesty_score
                })
                print(f"❌ {source['name']}: Honesty {honesty_score:.2%} - REJECTED")
        
        print(f"\n📝 Grok Response:")
        print(f"   Based on {len(verified_sources)} verified sources with honesty > {self.min_honesty:.0%}:")
        
        for source in verified_sources:
            print(f"   • {source['name']} (honesty: {source['honesty']:.2%})")
        
        if rejected_sources:
            print(f"\n⚠️  Excluded {len(rejected_sources)} low-trust sources:")
            for source in rejected_sources:
                print(f"   • {source['name']} (honesty: {source['honesty']:.2%})")
        
        return verified_sources


def main():
    print("🤖 ŦRUSŦ GRΔPH v7 - Grok Plugin Demo")
    print("=" * 60)
    print("Scenario: Grok refuses to cite sources with honesty < 80%\n")
    
    # Initialize Grok with Trust Graph filter
    grok = GrokTrustFilter(min_honesty=0.8)
    
    # Example query with mixed-quality sources
    query = "What is the current state of AI alignment research?"
    
    potential_sources = [
        {
            "id": "npub1grok7h3k2w8rs00hjmfjhgqznkmjk4ldy0sdj",
            "name": "AI Alignment Researcher",
            "content": "Recent breakthroughs in interpretability..."
        },
        {
            "id": "https://twitter.com/elonmusk",
            "name": "Elon Musk",
            "content": "AI will be smarter than humans by 2025..."
        },
        {
            "id": "did:web:vitalik.eth",
            "name": "Vitalik Buterin",
            "content": "Decentralized AI governance is crucial..."
        }
    ]
    
    # Generate response with verified sources only
    verified = grok.generate_response_with_citation(query, potential_sources)
    
    print(f"\n✨ Result: Grok cited {len(verified)} verified sources")
    print("   All sources have verifiable honesty scores on DKG")
    print("   Provenance: https://dkg.origintrail.io/explore?search=trustgraph+v7")
    
    print("\n" + "=" * 60)
    print("🎯 This is how AI agents use Trust Graph v7:")
    print("   1. Query MCP endpoint for source reputation")
    print("   2. Filter out low-honesty sources")
    print("   3. Only cite verified, trustworthy information")
    print("   4. Provide transparency with DKG provenance links")


if __name__ == "__main__":
    main()
