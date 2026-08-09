#!/bin/bash
# Pre-deployment check — all tests must pass before deploying.
# Usage: ./deploy.sh

set -e

echo "🧪 Running unit tests..."
echo "========================"

# Activate venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python -m pytest tests/ -v --tb=short

echo ""
echo "========================"
echo "✅ All tests passed! Safe to deploy."
echo ""

# Uncomment the lines below when AWS hosting is configured:
# echo "🚀 Deploying to AWS..."
# <deployment command here>
