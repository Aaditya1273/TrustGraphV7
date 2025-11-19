"""Stake Validator - Simulates NeuroWeb staking requirements"""

import math
from typing import Dict


class StakeValidator:
    """Validates and manages TRAC staking for Sybil resistance"""
    
    def __init__(self):
        self.stake_registry: Dict[str, float] = {}
        self.min_stake_for_high_trust = 100.0  # TRAC
        self.slashing_rate = 0.1  # 10%
    
    def register_stake(self, issuer: str, amount: float):
        """Register stake for an issuer"""
        self.stake_registry[issuer] = amount
        print(f"✓ Registered {amount} TRAC stake for {issuer[:12]}...")
    
    def get_stake(self, issuer: str) -> float:
        """Get stake amount for issuer"""
        return self.stake_registry.get(issuer, 0.0)
    
    def calculate_stake_weight(self, issuer: str) -> float:
        """Calculate stake weight multiplier (0.5x - 2.0x)"""
        stake = self.get_stake(issuer)
        
        # Logarithmic scaling: 100 TRAC = 1.0x, 1000 TRAC = 1.5x, 10000 TRAC = 2.0x
        if stake == 0:
            return 0.5  # Penalty for no stake
        if stake < 100:
            return 0.7
        
        weight = 1.0 + math.log10(stake / 100) * 0.5
        return min(weight, 2.0)  # Cap at 2x
    
    def can_publish_high_trust(self, issuer: str, trust_score: float) -> bool:
        """Check if issuer can publish high-trust atom"""
        if trust_score <= 0.7:
            return True  # No stake required for low/medium trust
        
        stake = self.get_stake(issuer)
        return stake >= self.min_stake_for_high_trust
    
    def simulate_dispute(self, issuer: str, fraudulent: bool = True) -> Dict:
        """Simulate dispute and slashing"""
        stake = self.get_stake(issuer)
        
        if fraudulent and stake > 0:
            slashed = stake * self.slashing_rate
            remaining = stake - slashed
            self.stake_registry[issuer] = remaining
            
            print(f"⚠️  Slashed {slashed} TRAC from {issuer[:12]}... ({remaining} remaining)")
            return {"slashed": slashed, "remaining": remaining}
        
        return {"slashed": 0, "remaining": stake}
    
    def get_stats(self) -> Dict:
        """Get staking statistics"""
        stakes = list(self.stake_registry.values())
        
        return {
            "totalStakers": len(self.stake_registry),
            "totalStaked": sum(stakes),
            "averageStake": sum(stakes) / len(stakes) if stakes else 0,
            "highStakers": len([s for s in stakes if s >= 1000])
        }
