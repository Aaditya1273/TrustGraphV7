#!/usr/bin/env python3
"""MCP Server - Model Context Protocol endpoint for AI agents"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from src.core.dkg_publisher import DKGPublisher
from src.core.trust_atom import TrustAtomV7, TrustVector

# Load environment variables
load_dotenv()

app = FastAPI(title="Trust Graph v7 MCP Server")
publisher = DKGPublisher()


# Request models
class QueryReputationRequest(BaseModel):
    target: str
    dimensions: Optional[List[str]] = None


class CheckThresholdRequest(BaseModel):
    target: str
    dimension: str
    threshold: float


class PublishAtomRequest(BaseModel):
    issuer: str
    target: str
    trust_vector: Dict
    content: str = ""


# x402 Payment middleware
def verify_payment(payment_proof: Optional[str], price: float) -> bool:
    """Verify x402 payment (simplified for demo)"""
    bypass_token = os.getenv("X402_BYPASS_TOKEN")
    
    if payment_proof == bypass_token:
        return True
    
    # In production: verify on-chain transaction
    return payment_proof and len(payment_proof) > 32


@app.get("/")
def root():
    return {
        "service": "Trust Graph v7 MCP Server",
        "version": "7.0.0",
        "protocol": "mcp"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Trust Graph v7 MCP Server"}


@app.get("/mcp/tools")
def get_tools():
    """MCP tool discovery"""
    return {
        "protocol": "mcp",
        "version": "1.0",
        "tools": [
            {
                "name": "query_reputation",
                "description": "Query aggregated reputation score for a target entity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "dimensions": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "check_trust_threshold",
                "description": "Check if target meets minimum trust threshold",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "dimension": {"type": "string"},
                        "threshold": {"type": "number"}
                    },
                    "required": ["target", "dimension", "threshold"]
                }
            },
            {
                "name": "publish_trust_atom",
                "description": "Publish a new Trust Atom to the DKG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issuer": {"type": "string"},
                        "target": {"type": "string"},
                        "trust_vector": {"type": "object"},
                        "content": {"type": "string"}
                    },
                    "required": ["issuer", "target"]
                }
            }
        ]
    }


@app.post("/mcp/query_reputation")
def query_reputation(
    request: QueryReputationRequest,
    x_payment_proof: Optional[str] = Header(None)
):
    """Query reputation (x402 protected)"""
    
    # Check payment
    if not verify_payment(x_payment_proof, 0.001):
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "protocol": "x402",
                "price": "0.001 USDC",
                "paymentAddress": os.getenv("X402_WALLET_ADDRESS", "0x742d35Cc..."),
                "instructions": "Include X-Payment-Proof header with transaction hash"
            }
        )
    
    reputation = publisher.get_aggregate_reputation(request.target)
    
    # Filter dimensions if requested
    if request.dimensions:
        filtered = {
            "target": reputation["target"],
            "atomCount": reputation["atomCount"]
        }
        for dim in request.dimensions:
            if dim in reputation:
                filtered[dim] = reputation[dim]
        return filtered
    
    return reputation


@app.post("/mcp/check_trust_threshold")
def check_trust_threshold(request: CheckThresholdRequest):
    """Check trust threshold (free endpoint)"""
    
    reputation = publisher.get_aggregate_reputation(request.target)
    
    # Simplified: use overall score for all dimensions
    score = reputation["averageOverall"]
    meets_threshold = score >= request.threshold
    
    return {
        "target": request.target,
        "dimension": request.dimension,
        "threshold": request.threshold,
        "score": score,
        "meetsThreshold": meets_threshold,
        "confidence": reputation["confidence"]
    }


@app.post("/mcp/publish_trust_atom")
def publish_trust_atom(request: PublishAtomRequest):
    """Publish Trust Atom"""
    
    try:
        atom = TrustAtomV7(
            issuer=request.issuer,
            target=request.target,
            trust_vector=TrustVector(**request.trust_vector),
            content=request.content
        )
        
        ka_id = publisher.publish_trust_atom(atom)
        
        return {
            "success": True,
            "kaId": ka_id,
            "atom": atom.to_jsonld()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_PORT", "3000"))
    
    print(f"🚀 Trust Graph v7 MCP Server starting on port {port}")
    print(f"\n📡 MCP Endpoints:")
    print(f"  GET  /mcp/tools - Tool discovery")
    print(f"  POST /mcp/query_reputation - Query reputation (x402 protected)")
    print(f"  POST /mcp/check_trust_threshold - Check trust threshold (free)")
    print(f"  POST /mcp/publish_trust_atom - Publish new atom")
    print(f"\n💡 Use with AI agents via Model Context Protocol\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
