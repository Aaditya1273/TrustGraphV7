#!/usr/bin/env python3
"""Trust Atom Publisher - Batch publish Trust Atoms to DKG"""

from src.core.dkg_publisher import DKGPublisher
from src.core.trust_atom import TrustAtomV7, TrustVector
from src.core.stake_validator import StakeValidator


def main():
    print("🚀 Trust Graph v7 - DKG Publisher\n")
    
    publisher = DKGPublisher()
    stake_validator = StakeValidator()
    
    # Simulate some stakers
    issuers = [
        "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
        "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH",
        "did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
    ]
    
    for i, issuer in enumerate(issuers):
        stake_validator.register_stake(issuer, 100 + i * 500)
    
    # Create sample Trust Atoms
    atoms = [
        TrustAtomV7(
            issuer=issuers[0],
            target="npub1grok7h3k2w8rs00hjmfjhgqznkmjk4ldy0sdj",
            trust_vector=TrustVector(
                honesty=0.98,
                expertise=0.95,
                bias=0.15,
                safety=0.99,
                speed=0.88,
                alignment=0.94,
                responsiveness=0.91,
                stake_weight=stake_validator.calculate_stake_weight(issuers[0])
            ),
            content="Exceptional AI alignment researcher with consistent accuracy",
            evidence_ka=["otobject:km1abc123"],
            required_stake="100",
            x402_config={
                "price": "0.001 USDC per query",
                "free": ["overall", "honesty", "safety"]
            }
        ),
        
        TrustAtomV7(
            issuer=issuers[1],
            target="https://twitter.com/elonmusk",
            trust_vector=TrustVector(
                honesty=0.72,
                expertise=0.95,
                bias=0.65,
                safety=0.80,
                speed=0.95,
                alignment=0.70,
                responsiveness=0.88,
                stake_weight=stake_validator.calculate_stake_weight(issuers[1])
            ),
            content="High expertise in tech/space, moderate bias in political content",
            required_stake="600"
        ),
        
        TrustAtomV7(
            issuer=issuers[2],
            target="did:web:vitalik.eth",
            trust_vector=TrustVector(
                honesty=0.96,
                expertise=0.98,
                bias=0.20,
                safety=0.95,
                speed=0.75,
                alignment=0.92,
                responsiveness=0.80,
                stake_weight=stake_validator.calculate_stake_weight(issuers[2])
            ),
            content="Ethereum founder, highly technical, balanced perspective",
            required_stake="1100",
            expires="2027-11-19T00:00:00Z"
        )
    ]
    
    print(f"\n📝 Publishing {len(atoms)} Trust Atoms...\n")
    
    results = publisher.publish_batch(atoms)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n✅ Successfully published: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print("\n📊 Published Knowledge Assets:")
        for r in successful:
            print(f"  - {r['kaId']}")
            print(f"    Target: {r['atom'].target}")
            print(f"    Overall: {r['atom'].overall:.3f}")
    
    print("\n📈 Stake Statistics:")
    print(stake_validator.get_stats())
    
    print("\n✨ Publisher Statistics:")
    print(publisher.get_stats())


if __name__ == "__main__":
    main()
