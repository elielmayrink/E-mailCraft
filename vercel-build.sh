#!/usr/bin/env bash
set -euo pipefail

echo "Installing backend Python dependencies..."
pip install -r backend/requirements.txt

echo "Build step completed."


