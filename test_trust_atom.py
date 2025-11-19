#!/usr/bin/env python3
"""Trust Atom v7 Tests"""

from src.core.trust_atom import TrustAtomV7, TrustVector


def test_basic_creation():
    """Test 1: Basic Trust Atom creation"""
    print("Test 1: Basic Trust Atom creation")
    
    atom = TrustAtomV7(
        issuer="did:key:z6Mk123",
        target="npub1test",
        trust_vector=TrustVector(honesty=0.9, expertise=0.8),
        content="Test atom"
    )
    
    assert atom.issuer == "did:key:z6Mk123"
    assert atom.target == "npub1test"
    assert 0 <= atom.overall <= 1
    print("✅ Pass\n")


def test_overall_calculation():
    """Test 2: Overall score calculation"""
    print("Test 2: Overall score calculation")
    
    atom = TrustAtomV7(
        issuer="did:key:z6Mk456",
        target="npub1test2",
        trust_vector=TrustVector(
            honesty=1.0,
            expertise=1.0,
            bias=0.0,
            safety=1.0,
            speed=1.0,
            alignment=1.0,
            responsiveness=1.0,
            stake_weight=1.0
        )
    )
    
    assert atom.overall > 0.95
    print(f"  Overall score: {atom.overall:.3f}")
    print("✅ Pass\n")


def test_stake_weight():
    """Test 3: Stake weight multiplier"""
    print("Test 3: Stake weight multiplier")
    
    atom1 = TrustAtomV7(
        issuer="did:key:z6Mk789",
        target="npub1test3",
        trust_vector=TrustVector(honesty=0.8, expertise=0.8, stake_weight=2.0)
    )
    
    atom2 = TrustAtomV7(
        issuer="did:key:z6Mk789",
        target="npub1test3",
        trust_vector=TrustVector(honesty=0.8, expertise=0.8, stake_weight=1.0)
    )
    
    assert atom1.overall > atom2.overall
    print(f"  2.0x stake: {atom1.overall:.3f}")
    print(f"  1.0x stake: {atom2.overall:.3f}")
    print("✅ Pass\n")


def test_validation():
    """Test 4: Validation"""
    print("Test 4: Validation")
    
    valid_atom = TrustAtomV7(
        issuer="did:key:z6Mk111",
        target="npub1valid",
        trust_vector=TrustVector(honesty=0.9),
        required_stake="200"
    )
    
    invalid_atom = TrustAtomV7(
        issuer="",
        target="npub1invalid"
    )
    
    assert valid_atom.is_valid() == True
    assert invalid_atom.is_valid() == False
    print("✅ Pass\n")


def test_jsonld_export():
    """Test 5: JSON-LD export"""
    print("Test 5: JSON-LD export")
    
    atom = TrustAtomV7(
        issuer="did:key:z6Mk222",
        target="npub1export",
        content="Export test"
    )
    
    jsonld = atom.to_jsonld()
    assert jsonld["@type"] == "VerifiableTrustAtom"
    assert jsonld["issuer"] == "did:key:z6Mk222"
    assert "trustVector" in jsonld
    print("✅ Pass\n")


def test_dkg_asset():
    """Test 6: DKG asset format"""
    print("Test 6: DKG asset format")
    
    atom = TrustAtomV7(
        issuer="did:key:z6Mk333",
        target="npub1dkg",
        trust_vector=TrustVector(honesty=0.95),
        evidence_ka=["otobject:km1"]
    )
    
    dkg_asset = atom.to_dkg_asset()
    assert "public" in dkg_asset
    assert "private" in dkg_asset
    # Check W3C Verifiable Credential format
    assert "@context" in dkg_asset["public"]
    assert "@type" in dkg_asset["public"]
    print("✅ Pass\n")


def main():
    print("🧪 Running Trust Atom v7 Tests\n")
    
    test_basic_creation()
    test_overall_calculation()
    test_stake_weight()
    test_validation()
    test_jsonld_export()
    test_dkg_asset()
    
    print("🎉 All tests passed!")


if __name__ == "__main__":
    main()
