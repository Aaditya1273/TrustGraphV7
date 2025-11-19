"""Trust Atom v7 - Multi-dimensional verifiable trust primitive"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, field_validator


class TrustVector(BaseModel):
    """8-dimensional trust vector"""
    honesty: float = Field(default=0.5, ge=0, le=1)
    expertise: float = Field(default=0.5, ge=0, le=1)
    bias: float = Field(default=0.5, ge=0, le=1)
    safety: float = Field(default=0.5, ge=0, le=1)
    speed: float = Field(default=0.5, ge=0, le=1)
    alignment: float = Field(default=0.5, ge=0, le=1)
    responsiveness: float = Field(default=0.5, ge=0, le=1)
    stake_weight: float = Field(default=1.0, ge=0.5, le=2.0)


class TrustAtomV7(BaseModel):
    """Multi-dimensional, revocable, stake-weighted trust primitive"""
    
    issuer: str
    target: str
    trust_vector: TrustVector = Field(default_factory=TrustVector)
    content: str = ""
    evidence_ka: List[str] = Field(default_factory=list)
    expires: Optional[str] = None
    replaces: Optional[str] = None
    required_stake: str = "0"
    x402_config: Optional[Dict] = None
    issued: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    @property
    def overall(self) -> float:
        """Calculate weighted overall score"""
        tv = self.trust_vector
        
        # Weighted average (bias is inverted - lower is better)
        score = (
            tv.honesty * 0.25 +
            tv.expertise * 0.20 +
            (1 - tv.bias) * 0.10 +
            tv.safety * 0.20 +
            tv.speed * 0.10 +
            tv.alignment * 0.15 +
            tv.responsiveness * 0.10
        )
        
        # Apply stake multiplier (capped at 2x)
        score *= min(tv.stake_weight, 2.0)
        
        return max(0.0, min(1.0, score))
    
    def to_jsonld(self) -> Dict:
        """Export as JSON-LD for DKG"""
        return {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://trustgraph.io/schemas/trust-atom-v7"
            ],
            "@type": "VerifiableTrustAtom",
            "issuer": self.issuer,
            "target": self.target,
            "trustVector": self.trust_vector.model_dump(),
            "overall": self.overall,
            "content": self.content,
            "evidenceKA": self.evidence_ka,
            "expires": self.expires,
            "replaces": self.replaces,
            "requiredStake": self.required_stake,
            "x402": self.x402_config,
            "issued": self.issued
        }
    
    def to_dkg_asset(self) -> Dict:
        """Convert to DKG Knowledge Asset format - Fixed protected term conflict"""
        import uuid
        atom_id = f"urn:trustgraph:atom:{uuid.uuid4()}"
        
        return {
            "public": {
                "@context": "http://schema.org/",
                "@id": atom_id,
                "@type": "CreativeWork",
                "name": f"Trust Atom: {self.target[:50]}",
                "description": self.content or "ŦRUSŦ GRΔPH v7 Multi-dimensional Trust Score",
                "author": {
                    "@type": "Person",
                    "@id": self.issuer,
                    "name": "TrustGraph Issuer"
                },
                "about": {
                    "@type": "Thing",
                    "@id": self.target,
                    "name": "Target Entity"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": str(self.overall),
                    "bestRating": "1.0",
                    "worstRating": "0.0",
                    "ratingCount": "1"
                },
                "datePublished": self.issued,
                "keywords": "trust,reputation,decentralized,verification"
            },
            "private": {
                "@context": "http://schema.org/",
                "@id": atom_id + "-private",
                "@type": "PropertyValue",
                "name": "Trust Vector Details",
                "value": str(self.trust_vector.model_dump()),
                "additionalProperty": [
                    {
                        "@type": "PropertyValue",
                        "name": "requiredStake",
                        "value": self.required_stake
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "expires",
                        "value": self.expires
                    }
                ]
            }
        }
    
    def is_valid(self) -> bool:
        """Validate Trust Atom"""
        if not self.issuer or not self.target:
            return False
        
        if not (0 <= self.overall <= 1):
            return False
        
        # Check expiration
        if self.expires:
            try:
                exp_date = datetime.fromisoformat(self.expires.replace('Z', '+00:00'))
                if exp_date < datetime.utcnow():
                    return False
            except:
                return False
        
        # High-trust atoms require stake
        if self.overall > 0.7:
            try:
                stake = float(self.required_stake.split()[0])
                if stake < 100:
                    return False
            except:
                return False
        
        return True
