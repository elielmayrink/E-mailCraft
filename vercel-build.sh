#!/usr/bin/env bash
set -euo pipefail

echo "Installing Python dependencies from api/requirements.txt..."
pip install -r api/requirements.txt

echo "Build step completed."


