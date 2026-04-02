@echo off
echo ========================================
echo Smart Money Intelligence Platform
echo EK CLICK SETUP - Sab Kuch Automatic!
echo ========================================
echo.

echo [Step 1/5] Dependencies install ho rahe hain...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Dependencies install nahi hui!
    echo Solution: Python properly install karo
    pause
    exit /b 1
)
echo ✓ Dependencies install ho gayi!
echo.

echo [Step 2/5] Packages check ho rahe hain...
python test_requirements.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Kuch packages missing hain!
    pause
    exit /b 1
)
echo.

echo [Step 3/5] Sample data generate ho raha hai...
echo (5-10 seconds lagenge)
python scripts/generate_sample_data.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Data generation mein problem!
    pause
    exit /b 1
)
echo.

echo [Step 4/5] Setup verify ho raha hai...
python verify_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Setup complete nahi hai!
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ SAB KUCH READY HAI!
echo ========================================
echo.
echo Ab dashboard khul raha hai...
echo Browser mein automatically khul jayega!
echo.
echo Dashboard band karne ke liye: Ctrl + C
echo ========================================
echo.

echo [Step 5/5] Dashboard start ho raha hai...
streamlit run dashboard/app.py

pause
