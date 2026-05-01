#!/usr/bin/env bash
# scripts/fallback.sh
# Use gemini-cli (or cursor-cli) when primary Ollama LLM limit is hit.
# Usage: bash scripts/fallback.sh "your prompt here"
# Requires: npm install -g @google/gemini-cli

set -e
PROMPT="${1:-Hello, who are you?}"
SYS=$(cat agent/prompts/system_prompt.md 2>/dev/null || echo "You are Profundus-Comet.")

echo "[fallback] Routing to gemini-cli..."
echo "[fallback] Prompt: $PROMPT"
echo ""

# Check which CLI is available
if command -v gemini &>/dev/null; then
    gemini --model gemini-2.5-pro \
           --system "$SYS" \
           --prompt "$PROMPT"
elif command -v cursor &>/dev/null; then
    cursor chat "$PROMPT"
elif command -v aichat &>/dev/null; then
    # aichat: https://github.com/sigoden/aichat
    aichat --model gemini:gemini-2.5-pro "$PROMPT"
else
    echo "[fallback] No CLI found. Installing gemini-cli..."
    npm install -g @google/gemini-cli
    echo "Run: gemini auth  # to authenticate"
    echo "Then re-run: bash scripts/fallback.sh "$PROMPT""
fi
