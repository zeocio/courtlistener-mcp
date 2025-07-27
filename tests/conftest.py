import pytest
import os
import sys
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
        'test_query': 'contract',
        'cluster_ids': [123456, 789012],
        'docket_ids': [65663213, 12345678],
        'person_ids': [8521, 12345]
    }

@pytest.fixture
def mcp_server():
    """MCP server fixture for integration tests."""
    from server_factory import create_courtlistener_server
    return create_courtlistener_server()
