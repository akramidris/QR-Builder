@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error

  echo Installing app dependencies...
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto :error
)

echo Installing PyInstaller...
.\.venv\Scripts\python.exe -m pip install pyinstaller
if errorlevel 1 goto :error

echo Building WhatsApp QR executable...
.\.venv\Scripts\python.exe -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name WhatsAppQR ^
  app.py
if errorlevel 1 goto :error

echo Build complete. EXE is in dist\WhatsAppQR.exe
exit /b 0

:error
echo Failed to build the executable.
pause
exit /b 1
