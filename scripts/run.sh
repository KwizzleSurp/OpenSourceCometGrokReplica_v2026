#!/usr/bin/env bash
# scripts/run.sh - Launch Profundus-Comet
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f .env ] && export $(grep -v '^#' .env | xargs)
[ -d .venv ] && source .venv/bin/activate
echo "Profundus-Comet | Model: ${OLLAMA_MODEL:-llama3.1:8b} | Ollama: ${OLLAMA_URL:-http://localhost:11434}"
python -m agent.core
