@echo off
setlocal
cd /d "%~dp0"
title Clock Pro Minimal - Fixed Builder

echo Checking Python...
where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or the py launcher is unavailable.
    pause
    exit /b 1
)

echo.
echo Installing required packages...
py -m pip install --upgrade PyQt6 pyinstaller
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)

echo.
echo Removing old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ClockPro.spec del /q ClockPro.spec

echo.
echo Building ClockPro.exe...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name ClockPro clock_pro.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo BUILD SUCCESSFUL
echo.
echo EXE:
echo %CD%\dist\ClockPro.exe
echo ==========================================
pause
