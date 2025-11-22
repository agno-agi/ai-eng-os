@echo off
REM Use this script to deploy Agent OS on Railway
REM Prerequisites:
REM - Railway CLI installed
REM - Railway account logged in via `railway login`

setlocal

echo 🚂 Starting Railway deployment...
echo.

REM Initialize a new project on Railway (uncomment if needed)
railway init -n "ai-eng-os"
if errorlevel 1 goto :error

echo 📦 Deploying PgVector database...
echo.
railway deploy -t 3jJFCA
if errorlevel 1 goto :error

echo ⏳ Waiting 10 seconds for database to be created...
echo.
timeout /t 10 /nobreak >nul

echo 🔧 Creating application service with environment variables...
echo.
railway add --service agent_os ^
  --variables "DB_DRIVER=postgresql+psycopg" ^
  --variables "DB_USER=${{pgvector.PGUSER}}" ^
  --variables "DB_PASS=${{pgvector.PGPASSWORD}}" ^
  --variables "DB_HOST=${{pgvector.PGHOST}}" ^
  --variables "DB_PORT=${{pgvector.PGPORT}}" ^
  --variables "DB_DATABASE=${{pgvector.PGDATABASE}}" ^
  --variables "OPENAI_API_KEY=%OPENAI_API_KEY%" ^
  --variables "PARALLEL_API_KEY=%PARALLEL_API_KEY%"
if errorlevel 1 goto :error

echo 🚀 Deploying application...
echo.
railway up --service agent_os -d
if errorlevel 1 goto :error

echo 🔗 Creating domain...
echo.
railway domain --service agent_os
if errorlevel 1 goto :error

echo.
echo Note: It may take up to 5 minutes for the domain to reach ready state while the application is deploying.
echo.

echo ✅ Deployment complete!
echo.
echo 💡 Tip: Run 'railway logs --service agent_os' to view your application logs.
echo.

pause
endlocal
goto :eof

:error
echo.
echo ❌ Deployment failed. Check the output above for errors.
echo.
pause
exit /b 1
