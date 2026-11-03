@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
title Assistente personale
python main.py %*
pause
