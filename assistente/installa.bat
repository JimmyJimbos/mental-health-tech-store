@echo off
cd /d "%~dp0"
echo === Installazione assistente ===
where py >nul 2>nul || (echo Installa prima Python 3.11 da python.org spuntando "Add to PATH" & pause & exit /b)
py -3.11 -m venv .venv || (echo Serve Python 3.11: scaricalo da python.org & pause & exit /b)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Installo le librerie per usare la scheda video (se fallisce funziona lo stesso col processore)
pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
if not exist .env copy .env.example .env
echo.
echo === Fatto. Ora apri il file .env e inserisci le chiavi (vedi README). ===
pause
