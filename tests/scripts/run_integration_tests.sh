#!/bin/bash
# Run only integration tests

echo "🧪 Running Integration Tests Only"
echo "================================="

if [[ -z "${COURTLISTENER_API_TOKEN}" ]]; then
    echo "❌ Error: COURTLISTENER_API_TOKEN required for integration tests"
    exit 1
fi

pytest tests/integration/ -m "integration" --tb=short -v
