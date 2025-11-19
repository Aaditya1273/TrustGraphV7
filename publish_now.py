#!/usr/bin/env python3
"""
REAL DKG Publisher - Publishes Trust Atoms to OriginTrail DKG
Run this AFTER configuring .env with your wallet credentials
"""

import os
from dotenv import load_dotenv
from src.core.dkg_publisher import DKGPublisher
from src.core.trust_atom import TrustAtomV7, TrustVector
from src.core.stake_validator import StakeValidator

# Load environment variables
load_dotenv()

def check_credentials():
    """Check if DKG credentials are configured"""
    priv_key = os.getenv("WALLET_PRIVATE_KEY")
    
    if not priv_key:
        print("❌ ERROR: DKG credentials not configured!")
        print("\n📋 TO FIX THIS:")
        print("1. Make sure .env file exists")
        print("2. Add your wallet private key:")
        print("   WALLET_PRIVATE_KEY=0x...")
        print("\n💡 Get testnet tokens from Discord bot")
        return False
    
    print("✅ DKG credentials found")
    print(f"   Private Key: {priv_key[:10]}...{priv_key[-8:]}")
    return True


def create_sample_atoms(stake_validator):
    """Create sample Trust Atoms for publishing"""
    
    # Sample issuers
    issuers = [
        "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
        "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH",
        "did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
    ]
    
    # Register stakes
    for i, issuer in enumerate(issuers):
        stake_validator.register_stake(issuer, 100 + i * 500)
    
    # Create atoms
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
            required_stake="100"
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
    
    return atoms


def main():
    print("🚀 ŦRUSŦ GRΔPH v7 - REAL DKG Publisher")
    print("=" * 60)
    
    # Check credentials
    if not check_credentials():
        return
    
    print("\n📊 Initializing components...")
    
    # Initialize
    publisher = DKGPublisher()
    stake_validator = StakeValidator()
    
    # Create atoms
    print("\n⚙️  Creating Trust Atoms...")
    atoms = create_sample_atoms(stake_validator)
    print(f"   Created {len(atoms)} Trust Atoms")
    
    # Publish
    print(f"\n📤 Publishing to DKG...")
    print("   This may take 1-2 minutes per atom")
    print()
    
    results = publisher.publish_batch(atoms)
    
    # Results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully published: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n📋 Published Knowledge Assets (UALs):")
        for r in successful:
            print(f"   • {r['kaId']}")
            print(f"     Target: {r['atom'].target}")
            print(f"     Overall: {r['atom'].overall:.3f}")
            print()
        
        print(f"🔍 View on DKG Explorer:")
        print(f"   https://dkg.origintrail.io/explore")
        print(f"   Search: trustgraph v7")
        
        # Save UALs
        import json
        with open('published_uals.json', 'w') as f:
            json.dump({
                "total": len(successful),
                "uals": [r['kaId'] for r in successful],
                "atoms": [r['atom'].to_jsonld() for r in successful]
            }, f, indent=2)
        print(f"\n💾 UALs saved to: published_uals.json")
    
    if failed:
        print(f"\n⚠️  Failed atoms:")
        for r in failed:
            print(f"   • {r['atom'].target}: {r['error']}")
    
    print(f"\n{'='*60}")
    print("✨ Publishing complete!")
    
    if successful:
        print("\n🎯 NEXT STEPS:")
        print("1. Copy UALs from published_uals.json")
        print("2. Add them to README.md")
        print("3. Verify on DKG Explorer")
        print("\n🏆 YOU NOW HAVE REAL DKG DATA!")


if __name__ == "__main__":
    main()
