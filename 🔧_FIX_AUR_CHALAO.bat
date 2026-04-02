@echo off
echo ========================================
echo   Smart Money Intelligence Platform
echo   FIX AUR CHALAO - Ek Click Mein!
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Python check kar rahe hain...
python --version
if errorlevel 1 (
    echo ❌ Python install nahi hai! Python 3.8+ install karo.
    pause
    exit /b 1
)
echo ✅ Python mil gaya!
echo.

echo [2/5] Pip upgrade kar rahe hain...
python -m pip install --upgrade pip --quiet
echo ✅ Pip upgraded!
echo.

echo [3/5] Streamlit aur sab packages install kar rahe hain...
echo (Thoda time lagega - 1-2 minute)
python -m pip install streamlit --upgrade --quiet
python -m pip install -r requirements.txt --quiet
echo ✅ Sab packages install ho gaye!
echo.

echo [4/5] Streamlit check kar rahe hain...
streamlit --version
if errorlevel 1 (
    echo ❌ Streamlit install nahi hua properly!
    echo Manually try karo: python -m pip install streamlit
    pause
    exit /b 1
)
echo ✅ Streamlit ready hai!
echo.

echo [5/5] Dashboard start kar rahe hain...
echo.
echo ========================================
echo   Dashboard khul raha hai browser mein!
echo   URL: http://localhost:8501
echo ========================================
echo.
echo Agar browser automatically nahi khula toh:
echo Manual browser mein jao aur type karo: localhost:8501
echo.
echo Dashboard band karne ke liye: Ctrl+C press karo
echo.

streamlit run dashboard/app.py

pause
