#!/bin/bash

# Use this script to patch/redeploy the agent_os service on Railway
# Prerequisites:
# - Railway CLI installed
# - Railway account logged in via `railway login`
# - Project already linked via `railway link`

set -e  # Exit on any error

echo -e "🚀 Patching agent_os service on Railway...\n"

# Deploy only the agent_os service with new code
railway up --service agent_os --environment production -d

echo -e "✅ Service patch complete!\n"
echo -e "💡 Tip: Run 'railway logs --service agent_os' to view your application logs.\n"

