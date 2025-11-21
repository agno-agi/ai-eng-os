#!/bin/bash

# Use this script to deploy Agent OS on Railway
# Prerequisites:
# - Railway CLI installed
# - Railway account logged in via `railway login`

set -e  # Exit on any error

# Load .env file if it exists
if [ -f .env ]; then
    echo -e "📄 .env file found...\n"
    set -a #run export command for all variables in .env file
    source .env
    set +a
fi

echo -e "🚂 Starting Railway deployment...\n"

# Initialize a new project on Railway (uncomment if needed)
railway init -n "agno"

echo -e "📦 Deploying PgVector database...\n"
railway deploy -t 3jJFCA

echo -e "⏳ Waiting 10 seconds for database to be created...\n"
sleep 10

echo -e "🔧 Creating application service...\n"
railway add --service agent_os

echo -e "📝 Setting environment variables...\n"
railway variables --set DB_DRIVER="postgresql+psycopg" --service agent_os
railway variables --set 'DB_USER=${{pgvector.PGUSER}}' --service agent_os
railway variables --set 'DB_PASS=${{pgvector.PGPASSWORD}}' --service agent_os
railway variables --set 'DB_HOST=${{pgvector.PGHOST}}' --service agent_os
railway variables --set 'DB_PORT=${{pgvector.PGPORT}}' --service agent_os
railway variables --set 'DB_DATABASE=${{pgvector.PGDATABASE}}' --service agent_os
railway variables --set "OPENAI_API_KEY=${OPENAI_API_KEY}" --service agent_os
railway variables --set "PARALLEL_API_KEY=${PARALLEL_API_KEY}" --service agent_os

echo -e "🚀 Deploying application...\n"
railway up --service agent_os -d

echo -e "🔗 Creating domain...\n"
railway domain --service agent_os

echo -e "Note: It may take up to 5 minutes for the domain to reach ready state while the application is deploying.\n"

echo -e "✅ Deployment complete!\n"
echo -e "💡 Tip: Run 'railway logs --service agent_os' to view your application logs.\n"
