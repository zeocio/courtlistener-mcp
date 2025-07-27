#!/bin/bash
# Run only unit tests

echo "🧪 Running Unit Tests Only"
echo "=========================="

pytest tests/unit/ -m "unit" --tb=short -v
