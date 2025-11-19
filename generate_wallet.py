#!/usr/bin/env python3
"""Generate a new Ethereum wallet for DKG"""

try:
    from web3 import Web3
    
    print("🔐 Generating new wallet...")
    print()
    
    w3 = Web3()
    account = w3.eth.account.create()
    
    print("✅ Wallet generated!")
    print()
    print("=" * 60)
    print("PUBLIC KEY (Address):")
    print(account.address)
    print()
    print("PRIVATE KEY:")
    print(account.key.hex())
    print("=" * 60)
    print()
    print("⚠️  SAVE THESE KEYS SECURELY!")
    print()
    print("📋 Next steps:")
    print("1. Copy these keys")
    print("2. Get testnet tokens: https://faucet.origintrail.io")
    print("3. Add to .env file:")
    print(f"   WALLET_PUBLIC_KEY={account.address}")
    print(f"   WALLET_PRIVATE_KEY={account.key.hex()}")
    print()
    print("4. Run: python publish_now.py")
    
except ImportError:
    print("❌ web3 not installed")
    print("Install it: pip install web3")
