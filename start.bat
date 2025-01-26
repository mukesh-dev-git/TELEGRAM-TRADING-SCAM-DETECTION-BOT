:: start.bat

@echo off

REM Activate Virtual Environment
call venv\Scripts\activate

REM Run the Telegram Scam Detection Bot
python src\main.py

REM Pause for Errors or Output
pause
