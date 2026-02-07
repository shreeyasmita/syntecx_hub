@echo off
setlocal

echo 🚀 Starting SynTeCX House Price Prediction Platform...

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
mkdir backend\ml\models 2>nul
mkdir backend\ml\data 2>nul
mkdir backend\logs 2>nul
mkdir frontend\node_modules 2>nul

REM Build and start services
echo 🐳 Building and starting Docker containers...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...

REM Check backend
curl -f http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running at http://localhost:8000
    echo    API Documentation: http://localhost:8000/docs
) else (
    echo ⚠️  Backend API may still be starting...
)

REM Check frontend
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running at http://localhost:3000
) else (
    echo ⚠️  Frontend may still be starting...
)

echo.
echo 🎉 SynTeCX Hub Platform Started Successfully!
echo.
echo Access the platform at:
echo   Frontend Dashboard: http://localhost:3000
echo   Backend API:        http://localhost:8000
echo   API Documentation:  http://localhost:8000/docs
echo.
echo To stop the platform, run: docker-compose down
echo To view logs, run: docker-compose logs -f

pause