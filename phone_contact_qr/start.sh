#!/usr/bin/env bash
set -euo pipefail

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv

  echo "Installing dependencies..."
  .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python app.py
