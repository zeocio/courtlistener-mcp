#!/bin/bash
# Run all CourtListener MCP tests

set -e

echo "🧪 Running All CourtListener MCP Tests"
echo "====================================="

# Check for API token
if [[ -z "${COURTLISTENER_API_TOKEN}" ]]; then
    echo "⚠️  Warning: COURTLISTENER_API_TOKEN not set"
    echo "   Some tests may be skipped"
    echo ""
fi

# Unit tests
echo "1️⃣ Running Unit Tests..."
pytest tests/unit/ -m "unit" --tb=short -v

# Integration tests  
echo "2️⃣ Running Integration Tests..."
pytest tests/integration/ -m "integration" --tb=short -v

# Functional tests
echo "3️⃣ Running Functional Tests..."
pytest tests/functional/ -m "functional" --tb=short -v

echo "✅ All tests completed!"
