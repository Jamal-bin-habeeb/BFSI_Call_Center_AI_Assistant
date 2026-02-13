@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting BFSI AI Assistant...
streamlit run src/app.py
pause
