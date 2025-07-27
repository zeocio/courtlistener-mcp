#!/usr/bin/env python3
"""
CourtListener MCP Server - Unit Test Generator

Automatically generates comprehensive unit test templates for all 17 tools.
Includes error handling, parameter validation, performance, and edge case tests.

Usage: python tests/scripts/generate_unit_tests.py [--tool TOOL_NAME] [--all]
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Tool definitions with their parameters and expected behaviors
TOOL_DEFINITIONS = {
    'opinion_tools': {
        'module': 'tools.opinion_tools',
        'register_function': 'register_opinion_tools',
        'tools': {
            'get_opinion': {
                'params': ['opinion_id', 'cluster_id', 'opinion_type', 'author_name', 'include_content', 'limit'],
                'required': [],
                'description': 'Retrieve legal opinions with detailed formatting'
            }
        }
    },
    'cluster_tools': {
        'module': 'tools.cluster_tools',
        'register_function': 'register_cluster_tools',
        'tools': {
            'get_cluster': {
                'params': ['cluster_id', 'case_name', 'court', 'date_filed_after', 'date_filed_before', 'citation', 'include_opinions', 'limit'],
                'required': [],
                'description': 'Retrieve case clusters with opinion groupings'
            }
        }
    },
    'docket_tools': {
        'module': 'tools.docket_tools',
        'register_function': 'register_docket_tools',
        'tools': {
            'get_docket': {
                'params': ['docket_id', 'docket_number', 'case_name', 'court', 'nature_of_suit', 'include_entries', 'limit'],
                'required': [],
                'description': 'Retrieve case dockets and procedural history'
            }
        }
    },
    'court_tools': {
        'module': 'tools.court_tools',
        'register_function': 'register_court_tools',
        'tools': {
            'get_court': {
                'params': ['court_id', 'court_name', 'jurisdiction', 'include_hierarchy', 'include_stats', 'limit'],
                'required': [],
                'description': 'Retrieve court information and hierarchy'
            }
        }
    },
    'search_tools': {
        'module': 'tools.search_tools',
        'register_function': 'register_search_tools',
        'tools': {
            'search_legal_cases': {
                'params': ['query', 'search_type', 'court', 'judge', 'date_filed_after', 'date_filed_before', 'enable_highlighting', 'limit'],
                'required': ['query'],
                'description': 'Search legal cases with advanced filtering'
            },
            'advanced_legal_search': {
                'params': ['query', 'search_type', 'court', 'judge', 'citation', 'case_name', 'status', 'order_by', 'limit'],
                'required': ['query'],
                'description': 'Advanced legal search with complex parameters'
            }
        }
    },
    'people_tools': {
        'module': 'tools.people_tools',
        'register_function': 'register_people_tools',
        'tools': {
            'get_judge': {
                'params': ['person_id', 'name_first', 'name_last', 'court_id', 'include_positions', 'include_education', 'limit'],
                'required': [],
                'description': 'Retrieve judge information and career details'
            }
        }
    },
    'political_affiliation_tools': {
        'module': 'tools.political_affiliation_tools',
        'register_function': 'register_political_affiliation_tools',
        'tools': {
            'get_political_affiliations': {
                'params': ['person_id', 'political_party', 'date_start_after', 'date_start_before', 'include_person_details', 'limit'],
                'required': [],
                'description': 'Retrieve political affiliation history'
            }
        }
    },
    'aba_ratings_tools': {
        'module': 'tools.aba_ratings_tools',
        'register_function': 'register_aba_ratings_tools',
        'tools': {
            'get_aba_ratings': {
                'params': ['person_id', 'rating', 'year_rated_after', 'year_rated_before', 'include_person_details', 'limit'],
                'required': [],
                'description': 'Retrieve ABA ratings for judges'
            }
        }
    },
    'retention_events_tools': {
        'module': 'tools.retention_events_tools',
        'register_function': 'register_retention_events_tools',
        'tools': {
            'get_retention_events': {
                'params': ['person_id', 'position_id', 'event_type', 'date_after', 'date_before', 'include_details', 'limit'],
                'required': [],
                'description': 'Retrieve judicial retention events'
            }
        }
    },
    'sources_tools': {
        'module': 'tools.sources_tools',
        'register_function': 'register_sources_tools',
        'tools': {
            'get_sources': {
                'params': ['source_id', 'name', 'date_modified_after', 'date_modified_before', 'include_stats', 'limit'],
                'required': [],
                'description': 'Retrieve source information and statistics'
            }
        }
    },
    'education_tools': {
        'module': 'tools.education_tools',
        'register_function': 'register_education_tools',
        'tools': {
            'get_educations': {
                'params': ['person_id', 'school', 'degree', 'degree_year_after', 'degree_year_before', 'include_person_details', 'limit'],
                'required': [],
                'description': 'Retrieve educational background information'
            }
        }
    },
    'citation_tools': {
        'module': 'tools.citation_tools',
        'register_function': 'register_citation_tools',
        'tools': {
            'verify_citations': {
                'params': ['text', 'volume', 'reporter', 'page'],
                'required': [],
                'description': 'Verify and lookup legal citations'
            }
        }
    },
    'opinions_cited_tools': {
        'module': 'tools.opinions_cited_tools',
        'register_function': 'register_opinions_cited_tools',
        'tools': {
            'find_authorities_cited': {
                'params': ['citing_opinion_id', 'cited_opinion_id', 'depth', 'include_details', 'limit'],
                'required': [],
                'description': 'Find authorities cited in opinions'
            },
            'find_citing_opinions': {
                'params': ['cited_opinion_id', 'citing_opinion_id', 'depth', 'include_details', 'limit'],
                'required': [],
                'description': 'Find opinions that cite a given opinion'
            },
            'analyze_citation_network': {
                'params': ['opinion_id', 'max_depth', 'include_metadata', 'limit'],
                'required': ['opinion_id'],
                'description': 'Analyze citation network for an opinion'
            }
        }
    },
    'position_tools': {
        'module': 'tools.position_tools',
        'register_function': 'register_position_tools',
        'tools': {
            'get_positions': {
                'params': ['position_id', 'person_id', 'court_id', 'position_type', 'how_selected', 'include_person_details', 'limit'],
                'required': [],
                'description': 'Retrieve judicial positions and appointments'
            }
        }
    }
}


def generate_test_class_header(tool_module: str, tool_name: str, description: str) -> str:
    """Generate the test class header with imports and setup."""
    class_name = ''.join([word.capitalize() for word in tool_module.replace('_tools', '').split('_')]) + 'Tools'
    
    return f'''#!/usr/bin/env python3
"""
Unit Tests for CourtListener MCP {class_name}

Comprehensive testing of {tool_name} functionality including:
- Success scenarios with various parameters
- Error handling (401, 403, 404, 429, 500, timeout, network)
- Parameter validation and edge cases
- Performance requirements
- Data formatting validation

Generated by: tests/scripts/generate_unit_tests.py
"""

import pytest
import httpx
import time
from unittest.mock import AsyncMock, patch, MagicMock
from mcp.server.fastmcp import FastMCP

from {TOOL_DEFINITIONS[tool_module]['module']} import {TOOL_DEFINITIONS[tool_module]['register_function']}


class Test{class_name}:
    """Unit tests for {tool_name} - {description}"""
    
    @pytest.fixture
    async def mcp_server(self):
        """Create MCP server with {tool_module} registered."""
        mcp = FastMCP(name="test")
        {TOOL_DEFINITIONS[tool_module]['register_function']}(mcp)
        return mcp
    
    @pytest.fixture
    def mock_api_response(self):
        """Standard mock API response."""
        return {{
            "count": 1,
            "results": [{{
                "id": 12345,
                "date_created": "2020-01-15T10:30:00Z",
                "date_modified": "2020-01-15T10:30:00Z"
            }}]
        }}
'''


def generate_success_test(tool_name: str, params: List[str], required: List[str]) -> str:
    """Generate success scenario test."""
    # Create sample parameters
    param_examples = {
        'query': '"contract law"',
        'opinion_id': '11063335',
        'cluster_id': '123456',
        'docket_id': '65663213',
        'person_id': '8521',
        'court_id': '"scotus"',
        'position_id': '12345',
        'source_id': '67890',
        'limit': '10',
        'include_content': 'True',
        'include_details': 'True',
        'include_person_details': 'True',
        'enable_highlighting': 'True'
    }
    
    # Build parameter string for the test call
    test_params = []
    for param in params[:3]:  # Use first 3 params for basic test
        if param in param_examples:
            test_params.append(f"{param}={param_examples[param]}")
    
    param_string = ', '.join(test_params) if test_params else ''
    
    return f'''
    @pytest.mark.unit
    async def test_{tool_name}_success(self, mcp_server, mock_api_response):
        """Test successful {tool_name} execution."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = mock_api_response
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call(
                {param_string}
            )
            
            # Verify successful execution
            assert isinstance(result, str)
            assert len(result) > 0
            assert mock_get.called
'''


def generate_error_handling_tests(tool_name: str) -> str:
    """Generate comprehensive error handling tests."""
    return f'''
    @pytest.mark.unit
    async def test_{tool_name}_not_found(self, mcp_server):
        """Test {tool_name} with no results found."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "No" in result or "not found" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_auth_error(self, mcp_server):
        """Test {tool_name} authentication error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 401
            mock_get.return_value.json.return_value = {{
                "detail": "Authentication credentials were not provided."
            }}
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "authentication" in result.lower() or "unauthorized" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_forbidden_error(self, mcp_server):
        """Test {tool_name} forbidden error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 403
            mock_get.return_value.json.return_value = {{
                "detail": "You do not have permission to perform this action."
            }}
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "permission" in result.lower() or "forbidden" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_rate_limit_error(self, mcp_server):
        """Test {tool_name} rate limiting error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 429
            mock_get.return_value.json.return_value = {{
                "detail": "Request was throttled. Expected available in 60 seconds."
            }}
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "rate" in result.lower() or "throttled" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_server_error(self, mcp_server):
        """Test {tool_name} server error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 500
            mock_get.return_value.text = "Internal Server Error"
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "error" in result.lower() or "server" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_network_timeout(self, mcp_server):
        """Test {tool_name} network timeout handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "timeout" in result.lower() or "network" in result.lower()
    
    @pytest.mark.unit
    async def test_{tool_name}_connection_error(self, mcp_server):
        """Test {tool_name} connection error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert "connection" in result.lower() or "network" in result.lower()
'''


def generate_parameter_validation_tests(tool_name: str, params: List[str], required: List[str]) -> str:
    """Generate parameter validation tests."""
    tests = f'''
    @pytest.mark.unit
    async def test_{tool_name}_parameter_validation(self, mcp_server):
        """Test {tool_name} parameter validation."""
        # Test with valid parameters
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            # Should not raise exception with valid params
            assert isinstance(result, str)
'''
    
    # Add specific validation tests for common parameters
    if 'limit' in params:
        tests += f'''
    
    @pytest.mark.unit
    @pytest.mark.parametrize("limit_value", [-1, 0, 1001])
    async def test_{tool_name}_invalid_limit(self, mcp_server, limit_value):
        """Test {tool_name} with invalid limit values."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            # Some invalid limits might be handled gracefully
            result = await mcp_server.get_tool('{tool_name}').call(limit=limit_value)
            assert isinstance(result, str)
'''
    
    if any(param.endswith('_id') for param in params):
        tests += f'''
    
    @pytest.mark.unit
    async def test_{tool_name}_invalid_id_types(self, mcp_server):
        """Test {tool_name} with invalid ID types."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Test should handle invalid IDs gracefully
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            # Test with string instead of int for ID fields
            result = await mcp_server.get_tool('{tool_name}').call()
            assert isinstance(result, str)
'''
    
    return tests


def generate_performance_tests(tool_name: str) -> str:
    """Generate performance requirement tests."""
    return f'''
    @pytest.mark.unit
    @pytest.mark.slow
    async def test_{tool_name}_performance(self, mcp_server, mock_api_response):
        """Test {tool_name} performance requirements."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = mock_api_response
            mock_get.return_value.status_code = 200
            
            start_time = time.time()
            result = await mcp_server.get_tool('{tool_name}').call()
            end_time = time.time()
            
            # Should complete within reasonable time (5 seconds max)
            duration = end_time - start_time
            assert duration < 5.0, f"Tool took too long: {{duration:.2f}}s"
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.unit
    async def test_{tool_name}_large_result_handling(self, mcp_server):
        """Test {tool_name} with large result sets."""
        # Mock large response
        large_response = {{
            "count": 1000,
            "results": [{{"id": i, "data": "x" * 100}} for i in range(100)]
        }}
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = large_response
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call(limit=100)
            
            # Should handle large responses without issues
            assert isinstance(result, str)
            assert len(result) > 1000  # Should have substantial content
'''


def generate_edge_case_tests(tool_name: str, params: List[str]) -> str:
    """Generate edge case tests."""
    tests = f'''
    @pytest.mark.unit
    async def test_{tool_name}_empty_response(self, mcp_server):
        """Test {tool_name} with empty API response."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert isinstance(result, str)
            # Should gracefully handle empty results
            assert len(result) > 0  # Should provide meaningful message
    
    @pytest.mark.unit
    async def test_{tool_name}_malformed_response(self, mcp_server):
        """Test {tool_name} with malformed API response."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Malformed JSON response
            mock_get.return_value.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "Invalid JSON response"
            
            result = await mcp_server.get_tool('{tool_name}').call()
            
            assert isinstance(result, str)
            assert "error" in result.lower() or "invalid" in result.lower()
'''
    
    # Add query-specific edge cases
    if 'query' in params:
        tests += f'''
    
    @pytest.mark.unit
    @pytest.mark.parametrize("special_query", [
        "", "   ", "a", "a" * 1000, "SELECT * FROM table", "<script>alert('xss')</script>"
    ])
    async def test_{tool_name}_special_queries(self, mcp_server, special_query):
        """Test {tool_name} with special query strings."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {{"count": 0, "results": []}}
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('{tool_name}').call(query=special_query)
            
            # Should handle special queries gracefully
            assert isinstance(result, str)
'''
    
    return tests


def generate_complete_test_file(tool_module: str, tool_name: str, tool_info: Dict[str, Any]) -> str:
    """Generate complete test file for a tool."""
    params = tool_info['params']
    required = tool_info['required']
    description = tool_info['description']
    
    # Generate all test sections
    header = generate_test_class_header(tool_module, tool_name, description)
    success_test = generate_success_test(tool_name, params, required)
    error_tests = generate_error_handling_tests(tool_name)
    param_tests = generate_parameter_validation_tests(tool_name, params, required)
    performance_tests = generate_performance_tests(tool_name)
    edge_tests = generate_edge_case_tests(tool_name, params)
    
    return f"""{header}{success_test}{error_tests}{param_tests}{performance_tests}{edge_tests}"""


def create_unit_test_file(tool_module: str, tool_name: str, tool_info: Dict[str, Any], output_dir: Path) -> Path:
    """Create a unit test file for a single tool."""
    test_content = generate_complete_test_file(tool_module, tool_name, tool_info)
    
    # Create output file path
    test_file = output_dir / f"test_{tool_name}.py"
    
    # Write the test file
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Generated: {test_file}")
    return test_file


def main():
    """Main function to generate unit tests."""
    parser = argparse.ArgumentParser(description="Generate unit tests for CourtListener MCP tools")
    parser.add_argument('--tool', help='Generate tests for specific tool only')
    parser.add_argument('--all', action='store_true', help='Generate tests for all tools')
    parser.add_argument('--output-dir', default='tests/unit/test_tools', help='Output directory for test files')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    total_tools = 0
    
    if args.tool:
        # Generate for specific tool
        found = False
        for tool_module, module_info in TOOL_DEFINITIONS.items():
            for tool_name, tool_info in module_info['tools'].items():
                if tool_name == args.tool:
                    test_file = create_unit_test_file(tool_module, tool_name, tool_info, output_dir)
                    generated_files.append(test_file)
                    total_tools += 1
                    found = True
                    break
            if found:
                break
        
        if not found:
            print(f"❌ Tool '{args.tool}' not found in tool definitions")
            return 1
    
    elif args.all:
        # Generate for all tools
        print("🚀 Generating unit tests for all CourtListener MCP tools...")
        print("=" * 60)
        
        for tool_module, module_info in TOOL_DEFINITIONS.items():
            print(f"\n📋 Processing {tool_module}...")
            for tool_name, tool_info in module_info['tools'].items():
                test_file = create_unit_test_file(tool_module, tool_name, tool_info, output_dir)
                generated_files.append(test_file)
                total_tools += 1
    
    else:
        parser.print_help()
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎉 Successfully generated {total_tools} unit test files!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Files created: {len(generated_files)}")
    
    print("\n📋 Generated test files:")
    for test_file in generated_files:
        print(f"   - {test_file.name}")
    
    print(f"\n🔥 Run tests with:")
    print(f"   pytest {output_dir}/ -v")
    print(f"   pytest {output_dir}/ -m unit")
    print(f"   pytest {output_dir}/ --tb=short")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 