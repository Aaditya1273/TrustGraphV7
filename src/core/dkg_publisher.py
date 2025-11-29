"""DKG Publisher - WORKING v8.1.0 for Hackathon"""

import os
import json
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DKGPublisher:
    """Publishes Trust Atoms to OriginTrail DKG v8 Testnet"""
    
    def __init__(self):
        # Check if DKG credentials are configured
        private_key = os.getenv("WALLET_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        # Ensure SDK-compatible env var is present
        if private_key and not os.getenv("PRIVATE_KEY"):
            os.environ["PRIVATE_KEY"] = private_key
        public_key = os.getenv("WALLET_PUBLIC_KEY") or os.getenv("PUBLIC_KEY")
        if public_key and not os.getenv("PUBLIC_KEY"):
            os.environ["PUBLIC_KEY"] = public_key
        
        if private_key:
            try:
                from dkg import DKG
                from dkg.providers import NodeHTTPProvider, BlockchainProvider
                
                # PUBLIC TESTNET NODE by default; prefer env overrides
                env_host = os.getenv("DKG_NODE_HOSTNAME")
                env_port = os.getenv("DKG_NODE_PORT")
                node_url = env_host or (f"http://localhost:{env_port}" if env_port else "http://v8-testnet-node.origintrail.io:8900")

                print("🔧 Initializing DKG v8 SDK...")
                print(f"   Node: {node_url}")
                print(f"   Blockchain: {os.getenv('DKG_BLOCKCHAIN_ID', 'otp:20430')}")
                
                # Create providers - blockchain_id is the ONLY required parameter
                node_provider = NodeHTTPProvider(endpoint_uri=node_url, api_version="v1")
                blockchain_provider = BlockchainProvider(
                    blockchain_id=os.getenv("DKG_BLOCKCHAIN_ID", "otp:20430")  # NeuroWeb testnet - environment is auto-derived
                )
                
                # SDK will automatically load PRIVATE_KEY from .env
                # No need to call set_account manually
                
                # Initialize DKG
                self.dkg = DKG(
                    node_provider=node_provider,
                    blockchain_provider=blockchain_provider
                )
                
                self.dkg_configured = True
                print("✅ DKG SDK initialized - REAL publishing enabled")
                
            except Exception as e:
                print(f"⚠️  DKG SDK error: {e}")
                print("   Falling back to local storage mode")
                self.dkg_configured = False
        else:
            print("⚠️  WALLET_PRIVATE_KEY not configured")
            print("   Using local storage mode")
            self.dkg_configured = False
        
        self.published_atoms = []
        self.local_storage_file = "local_atoms.json"
        
        # Load existing local atoms
        if os.path.exists(self.local_storage_file):
            try:
                with open(self.local_storage_file, 'r') as f:
                    data = json.load(f)
                    self.published_atoms = data.get("atoms", [])
                print(f"📂 Loaded {len(self.published_atoms)} existing atoms from local storage")
            except:
                pass
    
    def publish_trust_atom(self, trust_atom) -> str:
        """Publish single Trust Atom to DKG or local storage"""
        if not trust_atom.is_valid():
            raise ValueError("Invalid Trust Atom - cannot publish")
        
        asset = trust_atom.to_dkg_asset()
        
        print(f"Publishing: {trust_atom.issuer[:20]}... → {trust_atom.target[:20]}...")
        
        if self.dkg_configured:
            # REAL DKG v8 publishing
            try:
                # Publish to DKG testnet - correct format per SDK docs
                result = self.dkg.asset.create(
                    content=asset,  # Contains both 'public' and 'private' keys
                    options={
                        "epochs_num": 2,
                        "minimum_number_of_finalization_confirmations": 3,
                        "minimum_number_of_node_replications": 1
                    }
                )
                
                # Get UAL from result
                ual = result.get("UAL") or result.get("assertionId")
                print(f"✅ REAL DKG PUBLISH SUCCESS! UAL: {ual}")
                
                self.published_atoms.append({
                    "kaId": ual,
                    "trustAtom": trust_atom.to_jsonld(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": "DKG_TESTNET"
                })
                
                return ual
                
            except Exception as error:
                print(f"❌ DKG publish failed: {error}")
                print("   Falling back to local storage")
                return self._publish_local(trust_atom, asset)
        else:
            # Local storage mode
            return self._publish_local(trust_atom, asset)
    
    def _publish_local(self, trust_atom, asset) -> str:
        """Publish to local storage (fallback)"""
        import hashlib
        
        # Generate local ID
        content = json.dumps(asset, sort_keys=True)
        local_id = f"local:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
        
        print(f"💾 Saved locally: {local_id}")
        
        self.published_atoms.append({
            "kaId": local_id,
            "trustAtom": trust_atom.to_jsonld(),
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "LOCAL"
        })
        
        # Save to file
        self._save_local_atoms()
        
        return local_id
    
    def _save_local_atoms(self):
        """Save atoms to local JSON file"""
        with open(self.local_storage_file, 'w') as f:
            json.dump({
                "total": len(self.published_atoms),
                "atoms": self.published_atoms
            }, f, indent=2)
    
    def publish_batch(self, trust_atoms: List) -> List[Dict]:
        """Publish multiple Trust Atoms"""
        results = []
        
        for atom in trust_atoms:
            try:
                ka_id = self.publish_trust_atom(atom)
                results.append({"success": True, "kaId": ka_id, "atom": atom})
            except Exception as e:
                results.append({"success": False, "error": str(e), "atom": atom})
        
        return results
    
    def query_trust_atoms(self, target_id: str) -> List[Dict]:
        """Query Trust Atoms for a target"""
        if self.dkg_configured:
            # REAL DKG query (TODO: implement when SDK supports it)
            return self._query_local(target_id)
        else:
            # Local query
            return self._query_local(target_id)
    
    def _query_local(self, target_id: str) -> List[Dict]:
        """Query local storage"""
        results = []
        for atom_data in self.published_atoms:
            atom = atom_data.get("trustAtom", {})
            if atom.get("target") == target_id:
                results.append({
                    "atom": atom_data.get("kaId"),
                    "issuer": atom.get("issuer"),
                    "overall": atom.get("overall"),
                    "content": atom.get("content")
                })
        
        return sorted(results, key=lambda x: x.get("overall", 0), reverse=True)
    
    def get_aggregate_reputation(self, target_id: str) -> Dict:
        """Get aggregated reputation for target"""
        atoms = self.query_trust_atoms(target_id)
        
        if not atoms:
            return {
                "target": target_id,
                "atomCount": 0,
                "averageOverall": 0.0,
                "confidence": 0.0
            }
        
        overall_scores = [float(a["overall"]) for a in atoms]
        average = sum(overall_scores) / len(overall_scores)
        
        # Confidence increases with more atoms (logarithmic)
        import math
        confidence = min(1.0, math.log10(len(atoms) + 1) / 2)
        
        return {
            "target": target_id,
            "atomCount": len(atoms),
            "averageOverall": average,
            "confidence": confidence,
            "atoms": atoms[:10]
        }
    
    def get_stats(self) -> Dict:
        """Get publisher statistics"""
        dkg_count = len([a for a in self.published_atoms if a.get("mode") == "DKG_TESTNET"])
        local_count = len([a for a in self.published_atoms if a.get("mode") == "LOCAL"])
        
        return {
            "totalPublished": len(self.published_atoms),
            "dkgPublished": dkg_count,
            "localPublished": local_count,
            "mode": "DKG_TESTNET" if self.dkg_configured else "LOCAL",
            "atoms": self.published_atoms
        }
