@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error

  echo Installing dependencies...
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :error
)

start "" ".\.venv\Scripts\pythonw.exe" "app.py"
exit /b 0

:error
echo Failed to start the app.
pause
exit /b 1
