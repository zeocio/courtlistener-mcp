# CourtListener MCP Server - Proposed Test Directory Structure

## Current State Analysis

### Existing Test Files
- `tests/courtlistener_evals.py` (806 lines) - Comprehensive evaluation suite
- `tests/mcp_test_runner.py` (545 lines) - MCP tool test runner
- `tests/test_config.sh` (262 lines) - Test configuration script
- `tests/evaluation_checklist.md` (360 lines) - Manual evaluation checklist
- `test_search_pagination.py` (447 lines) - Search pagination tests **(NEW)**
- `demo_live_search_results.py` (318 lines) - Live search demo **(NEW)**
- `test_courtlistener_client.py` (54 lines) - Simple client test

### Issues with Current Structure
1. **Mixed Locations**: Test files scattered between root and `tests/` folder
2. **Unclear Categorization**: No separation between unit, integration, and functional tests
3. **Inconsistent Naming**: Various naming patterns for test files
4. **Missing Organization**: No clear structure for different test types
5. **Documentation Scattered**: Test results and docs mixed with code

## Proposed Directory Structure

```
tests/
├── README.md                           # Testing documentation
├── conftest.py                         # pytest configuration
├── pytest.ini                         # pytest settings
└── requirements-test.txt               # Test-specific dependencies

├── unit/                               # Unit tests (isolated component testing)
│   ├── __init__.py
│   ├── test_tools/                     # Individual tool unit tests
│   │   ├── __init__.py
│   │   ├── test_opinion_tools.py       # Opinion tool unit tests
│   │   ├── test_cluster_tools.py       # Cluster tool unit tests
│   │   ├── test_docket_tools.py        # Docket tool unit tests
│   │   ├── test_court_tools.py         # Court tool unit tests
│   │   ├── test_search_tools.py        # Search tool unit tests
│   │   ├── test_people_tools.py        # People tool unit tests
│   │   └── test_citation_tools.py      # Citation tool unit tests
│   ├── test_core/                      # Core functionality unit tests
│   │   ├── __init__.py
│   │   ├── test_lifespan.py           # Lifespan management tests
│   │   └── test_server_factory.py      # Server factory tests
│   └── test_utils/                     # Utility function unit tests
│       ├── __init__.py
│       ├── test_formatters.py          # Formatter unit tests
│       └── test_mappings.py            # Mapping unit tests

├── integration/                        # Integration tests (component interaction)
│   ├── __init__.py
│   ├── test_mcp_server.py             # MCP server integration tests
│   ├── test_api_integration.py        # CourtListener API integration
│   ├── test_tool_workflows.py         # Multi-tool workflow tests
│   └── test_authentication.py         # Authentication integration tests

├── functional/                         # Functional tests (end-to-end scenarios)
│   ├── __init__.py
│   ├── test_search_functionality.py   # Search feature tests (NEW location)
│   ├── test_pagination.py             # Pagination tests (NEW location)
│   ├── test_search_pagination.py      # Combined search+pagination (MOVED)
│   ├── test_legal_workflows.py        # Legal research workflows
│   └── test_performance.py            # Performance and load tests

├── demos/                              # Demo and example tests
│   ├── __init__.py
│   ├── demo_basic_usage.py            # Basic usage examples
│   ├── demo_live_search.py            # Live search demo (MOVED)
│   ├── demo_advanced_features.py     # Advanced feature demos
│   └── demo_client_examples.py       # Client usage examples

├── fixtures/                           # Test data and fixtures
│   ├── __init__.py
│   ├── sample_data/                   # Sample API responses
│   │   ├── opinions.json
│   │   ├── clusters.json
│   │   ├── courts.json
│   │   └── search_results.json
│   ├── test_data.py                   # Test data constants
│   └── mock_responses.py              # Mock API response generators

├── config/                             # Test configuration
│   ├── __init__.py
│   ├── test_settings.py               # Test configuration settings
│   ├── environments.py                # Different test environments
│   └── test_config.yaml               # YAML configuration file

├── utils/                              # Test utilities
│   ├── __init__.py
│   ├── test_helpers.py                # Common test helper functions
│   ├── mcp_client.py                  # Test MCP client wrapper
│   ├── assertions.py                  # Custom assertion helpers
│   └── mock_server.py                 # Mock server utilities

├── evaluation/                         # Comprehensive evaluation suites
│   ├── __init__.py
│   ├── comprehensive_eval.py          # Full evaluation suite (MOVED from courtlistener_evals.py)
│   ├── evaluation_checklist.md        # Manual checklist (MOVED)
│   ├── benchmarks.py                  # Performance benchmarks
│   └── quality_metrics.py             # Code quality metrics

├── scripts/                            # Test runner scripts
│   ├── run_all_tests.sh               # Run all test suites
│   ├── run_unit_tests.sh              # Run only unit tests
│   ├── run_integration_tests.sh       # Run only integration tests
│   ├── run_functional_tests.sh        # Run only functional tests
│   ├── test_with_coverage.sh          # Run tests with coverage
│   └── ci_test_runner.sh              # CI/CD test runner

└── results/                            # Test results and reports
    ├── .gitignore                     # Ignore test result files
    ├── latest/                        # Latest test run results
    └── archived/                      # Archived test results
        └── {timestamp}/               # Results by timestamp
```

## Detailed File Organization

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**New Files to Create**:
- `test_tools/test_search_tools.py` - Unit tests for search tool functions
- `test_core/test_lifespan.py` - Test lifespan management
- `test_utils/test_formatters.py` - Test result formatting functions

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and API integration

**Files to Create**:
- `test_mcp_server.py` - Test MCP server initialization and tool registration
- `test_api_integration.py` - Test CourtListener API communication
- `test_tool_workflows.py` - Test multi-tool workflows

### 3. Functional Tests (`tests/functional/`)

**Purpose**: End-to-end feature testing

**Files to Move/Create**:
- **MOVE** `test_search_pagination.py` → `tests/functional/test_search_pagination.py`
- **CREATE** `test_search_functionality.py` - Focused search feature tests
- **CREATE** `test_pagination.py` - Isolated pagination tests

### 4. Demos (`tests/demos/`)

**Purpose**: Demonstration and example code

**Files to Move**:
- **MOVE** `demo_live_search_results.py` → `tests/demos/demo_live_search.py`
- **MOVE** `test_courtlistener_client.py` → `tests/demos/demo_client_examples.py`

### 5. Evaluation (`tests/evaluation/`)

**Purpose**: Comprehensive evaluation and quality assessment

**Files to Move**:
- **MOVE** `tests/courtlistener_evals.py` → `tests/evaluation/comprehensive_eval.py`
- **MOVE** `tests/evaluation_checklist.md` → `tests/evaluation/evaluation_checklist.md`

## Configuration Files

### `tests/pytest.ini`
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests  
    functional: Functional tests
    slow: Slow running tests
    requires_api: Tests requiring API token
```

### `tests/conftest.py`
```python
import pytest
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def api_token():
    """API token fixture."""
    return os.getenv('COURTLISTENER_API_TOKEN')

@pytest.fixture
def test_data():
    """Common test data fixture."""
    return {
        'opinion_ids': [11063335, 2812209],
        'court_ids': ['scotus', 'ca9', 'dcd'],
        'test_query': 'contract'
    }
```

## Test Runner Scripts

### `tests/scripts/run_all_tests.sh`
```bash
#!/bin/bash
echo "🧪 Running All CourtListener MCP Tests"
echo "====================================="

# Unit tests
echo "1️⃣ Running Unit Tests..."
pytest tests/unit/ -m "unit" --tb=short

# Integration tests  
echo "2️⃣ Running Integration Tests..."
pytest tests/integration/ -m "integration" --tb=short

# Functional tests
echo "3️⃣ Running Functional Tests..."
pytest tests/functional/ -m "functional" --tb=short

echo "✅ All tests completed!"
```

## Benefits of This Structure

### 1. **Clear Separation of Concerns**
- Unit tests focus on individual components
- Integration tests cover component interactions
- Functional tests validate end-to-end features

### 2. **Improved Test Discovery**
- Consistent naming patterns (`test_*.py`)
- Logical grouping by test type
- Clear separation of test code from demo code

### 3. **Better Maintainability**
- Related tests grouped together
- Shared utilities and fixtures organized
- Configuration centralized

### 4. **Enhanced CI/CD Support**
- Separate scripts for different test types
- Configurable test execution
- Results organized and archivable

### 5. **Developer Experience**
- Easy to find relevant tests
- Clear documentation structure
- Consistent patterns across test types

## Migration Plan

### Phase 1: Create Structure
1. Create new directory structure
2. Add configuration files (`pytest.ini`, `conftest.py`)
3. Create test utility modules

### Phase 2: Move Existing Files
1. Move `test_search_pagination.py` to `tests/functional/`
2. Move `demo_live_search_results.py` to `tests/demos/`
3. Move evaluation files to `tests/evaluation/`

### Phase 3: Refactor and Enhance
1. Split large test files into focused modules
2. Create proper unit tests for individual tools
3. Add integration tests for API communication

### Phase 4: Add Infrastructure
1. Create test runner scripts
2. Set up result archiving
3. Add coverage reporting

## Usage Examples

### Running Specific Test Types
```bash
# Unit tests only
pytest tests/unit/

# Integration tests with API token required
pytest tests/integration/ -m "requires_api"

# Functional tests for search features
pytest tests/functional/test_search_functionality.py

# All tests with coverage
pytest --cov=. --cov-report=html tests/
```

### Running the New Search Pagination Tests
```bash
# Run all search-related tests
pytest tests/functional/test_search_pagination.py -v

# Run with live API data
COURTLISTENER_API_TOKEN=your_token pytest tests/functional/ -m "requires_api"
```

This structure provides a professional, scalable foundation for testing the CourtListener MCP server while maintaining all existing functionality and improving organization significantly. 