# CourtListener MCP Server - Test Suite

This directory contains comprehensive tests for the CourtListener MCP Server.

## Directory Structure

- **`unit/`** - Unit tests for individual components
- **`integration/`** - Integration tests for component interactions
- **`functional/`** - End-to-end functional tests
- **`demos/`** - Demo scripts and usage examples
- **`fixtures/`** - Test data and mock responses
- **`config/`** - Test configuration files
- **`utils/`** - Test utility functions
- **`evaluation/`** - Comprehensive evaluation suites
- **`scripts/`** - Test runner scripts
- **`results/`** - Test results and reports

## Running Tests

### Quick Start
```bash
# Run all tests
./scripts/run_all_tests.sh

# Run specific test types
./scripts/run_unit_tests.sh
./scripts/run_integration_tests.sh
./scripts/run_functional_tests.sh
```

### Using pytest directly
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Tests requiring API token
pytest -m "requires_api"

# With coverage
pytest --cov=. --cov-report=html
```

## Configuration

Set the following environment variables:

- `COURTLISTENER_API_TOKEN` - Required for integration and functional tests
- `TEST_MODE` - Test mode: 'basic', 'full', 'integration'

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.functional` - Functional tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_api` - Tests requiring API token
