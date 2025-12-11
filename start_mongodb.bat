@echo off
echo Starting MongoDB...

REM Check if MongoDB is installed
where mongod >nul 2>nul
if %errorlevel% neq 0 (
    echo MongoDB is not installed or not in PATH
    echo Please install MongoDB from: https://www.mongodb.com/try/download/community
    pause
    exit /b 1
)

REM Create data directory if it doesn't exist
if not exist "C:\data\db" (
    echo Creating MongoDB data directory...
    mkdir "C:\data\db"
)

echo Starting MongoDB server...
mongod --dbpath "C:\data\db"

pause