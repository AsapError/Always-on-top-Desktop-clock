@echo off
cd /d "%~dp0"

echo Starting Clock Pro...
py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo INSTALL FAILED.
    pause
    exit /b 1
)

echo.
echo Starting application...
py clock_pro.py

echo.
echo Clock Pro closed.
pause
