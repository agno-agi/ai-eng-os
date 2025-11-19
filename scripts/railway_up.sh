#!/bin/bash

# Use this script to deploy Agent OS on Railway
# Prerequisites:
# - Railway CLI installed
# - Railway account logged in via `railway login`

set -e  # Exit on any error

echo "🚂 Starting Railway deployment..."

# Initialize a new project on Railway (uncomment if needed)
railway init -n "agno"

# Deploy PgVector database first (it needs to exist before we reference it)
echo "📦 Deploying PgVector database..."
railway deploy -t 3jJFCA

# Wait for database to be provisioned
echo "⏳ Waiting 10 seconds for database to be created..."
sleep 10

# Create the application service with environment variables already set
echo "🔧 Creating application service with environment variables..."
railway add --service agent_os \
  --variables "DB_DRIVER=postgresql+psycopg" \
  --variables 'DB_USER=${{pgvector.PGUSER}}' \
  --variables 'DB_PASS=${{pgvector.PGPASSWORD}}' \
  --variables 'DB_HOST=${{pgvector.PGHOST}}' \
  --variables 'DB_PORT=${{pgvector.PGPORT}}' \
  --variables 'DB_DATABASE=${{pgvector.PGDATABASE}}' \
  --variables "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"

# Deploy the application
echo "🚀 Deploying application..."
railway up --service agent_os -d

echo "🔗 Creating domain..."
railway domain --service agent_os

echo "Note: It may take upto 5 minutes for the domain to reach ready state while the application is deploying."

echo "✅ Deployment complete!"
echo "💡 Tip: Run 'railway logs --service agent_os' to view your application logs"