#!/bin/bash
# Run tests with coverage report

echo "🧪 Running Tests with Coverage"
echo "=============================="

pytest --cov=. --cov-report=html --cov-report=term tests/
echo "📊 Coverage report generated in htmlcov/"
