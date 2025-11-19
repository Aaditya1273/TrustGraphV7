#!/bin/bash
# Deploy MCP Server to Fly.io (Free Tier)

echo "🚀 Deploying ŦRUSŦ GRΔPH v7 MCP Server to Fly.io"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# Login to Fly.io
echo "🔐 Logging in to Fly.io..."
flyctl auth login

# Create fly.toml if it doesn't exist
if [ ! -f "fly.toml" ]; then
    echo "📝 Creating fly.toml..."
    cat > fly.toml << 'EOF'
app = "trustgraph-v7-mcp"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "3000"
  MCP_PORT = "3000"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
EOF
fi

# Create Procfile for deployment
echo "📝 Creating Procfile..."
cat > Procfile << 'EOF'
web: python mcp_server.py
EOF

# Set secrets
echo "🔐 Setting environment secrets..."
flyctl secrets set \
  DKG_NODE_HOSTNAME="$DKG_NODE_HOSTNAME" \
  WALLET_PUBLIC_KEY="$WALLET_PUBLIC_KEY" \
  WALLET_PRIVATE_KEY="$WALLET_PRIVATE_KEY" \
  X402_WALLET_ADDRESS="$X402_WALLET_ADDRESS"

# Deploy
echo "🚀 Deploying to Fly.io..."
flyctl deploy

# Get URL
echo ""
echo "✅ Deployment complete!"
echo "🌐 Your MCP server is live at:"
flyctl info --json | jq -r '.Hostname' | xargs -I {} echo "   https://{}"
echo ""
echo "📋 Add this URL to your README.md"
