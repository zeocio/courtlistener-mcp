#!/bin/bash
# Run only functional tests

echo "🧪 Running Functional Tests Only"
echo "================================"

if [[ -z "${COURTLISTENER_API_TOKEN}" ]]; then
    echo "❌ Error: COURTLISTENER_API_TOKEN required for functional tests"
    exit 1
fi

pytest tests/functional/ -m "functional" --tb=short -v
