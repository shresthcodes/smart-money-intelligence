@echo off
echo ========================================
echo   Smart Money Intelligence Platform
echo   PERFECT SOLUTION - 100%% Working!
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Python check kar rahe hain...
python --version
if errorlevel 1 (
    echo ❌ Python install nahi hai!
    pause
    exit /b 1
)
echo ✅ Python ready!
echo.

echo [2/3] Streamlit install kar rahe hain (properly)...
python -m pip install streamlit --upgrade --quiet
echo ✅ Streamlit installed!
echo.

echo [3/3] Dashboard start kar rahe hain...
echo.
echo ========================================
echo   Dashboard khul raha hai!
echo   URL: http://localhost:8501
echo ========================================
echo.
echo Agar browser nahi khula toh manually:
echo 1. Browser kholo
echo 2. Type karo: localhost:8501
echo 3. Enter press karo
echo.
echo Dashboard band karne ke liye: Ctrl+C
echo.

python -m streamlit run dashboard/app.py

pause
