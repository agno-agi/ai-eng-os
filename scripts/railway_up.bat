@echo off
REM Use this script to deploy Agent OS on Railway
REM Prerequisites:
REM - Railway CLI installed
REM - Railway account logged in via `railway login`

echo 🚂 Starting Railway deployment...
echo.

REM Initialize a new project on Railway
railway init -n "agno"

echo 📦 Deploying PgVector database...
echo.
railway add -d postgres -t 3jJFCA --name pgvector

echo ⏳ Waiting 30 seconds for database to be fully ready...
echo.
timeout /t 30 /nobreak

echo 🔧 Creating application service with environment variables...
echo.
railway add --name agent_os

REM Set environment variables for the agent_os service
railway variables set --service agent_os DB_DRIVER="postgresql+psycopg" DB_USER="${{pgvector.PGUSER}}" DB_PASS="${{pgvector.PGPASSWORD}}" DB_HOST="${{pgvector.PGHOST}}" DB_PORT="${{pgvector.PGPORT}}" DB_DATABASE="${{pgvector.PGDATABASE}}" OPENAI_API_KEY="%OPENAI_API_KEY%" PARALLEL_API_KEY="%PARALLEL_API_KEY%"

echo 🚀 Deploying application...
echo.
railway up --service agent_os -d

echo 🔗 Creating domain...
echo.
railway domain --service agent_os

echo.
echo 📝 Note: It may take up to 5 minutes for the domain to reach ready state while the application is deploying.
echo.

echo ✅ Deployment complete!
echo.

echo 💡 Tip: Run 'railway logs --service agent_os' to view your application logs.
echo.

pause