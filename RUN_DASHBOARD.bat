@echo off
echo ========================================
echo   Smart Money Intelligence Dashboard
echo   Browser pe khul raha hai...
echo ========================================
echo.

REM Skip Streamlit email prompt
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Run dashboard
python -m streamlit run dashboard/app.py --server.headless true

pause
