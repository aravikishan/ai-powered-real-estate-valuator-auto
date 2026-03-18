#!/bin/bash
set -e
echo "Starting AI-Powered Real Estate Valuator..."
uvicorn app:app --host 0.0.0.0 --port 9107 --workers 1
