#!/usr/bin/env python3
"""
CourtListener MCP Server - Error Handling Test Framework

Comprehensive error scenario testing framework for all MCP tools.
Provides standardized error injection and validation across all tools.

Usage:
    from tests.utils.error_test_framework import ErrorTestFramework
    
    framework = ErrorTestFramework()
    await framework.test_all_error_scenarios(tool_name, mcp_server)
"""

import asyncio
import httpx
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Standard error types to test across all tools."""
    AUTHENTICATION_ERROR = "401_auth"
    FORBIDDEN_ERROR = "403_forbidden"
    NOT_FOUND_ERROR = "404_not_found"
    RATE_LIMIT_ERROR = "429_rate_limit"
    SERVER_ERROR = "500_server"
    BAD_GATEWAY = "502_bad_gateway"
    SERVICE_UNAVAILABLE = "503_service_unavailable"
    GATEWAY_TIMEOUT = "504_gateway_timeout"
    NETWORK_TIMEOUT = "timeout_error"
    CONNECTION_ERROR = "connection_error"
    SSL_ERROR = "ssl_error"
    DNS_ERROR = "dns_error"
    MALFORMED_JSON = "malformed_json"
    EMPTY_RESPONSE = "empty_response"
    INVALID_CONTENT_TYPE = "invalid_content_type"


@dataclass
class ErrorScenario:
    """Definition of an error scenario to test."""
    error_type: ErrorType
    status_code: Optional[int]
    response_data: Optional[Dict[str, Any]]
    exception_class: Optional[type]
    exception_message: Optional[str]
    expected_in_result: List[str]
    description: str


class ErrorTestFramework:
    """Framework for comprehensive error testing across all MCP tools."""
    
    def __init__(self):
        self.error_scenarios = self._define_error_scenarios()
    
    def _define_error_scenarios(self) -> Dict[ErrorType, ErrorScenario]:
        """Define all standard error scenarios to test."""
        return {
            ErrorType.AUTHENTICATION_ERROR: ErrorScenario(
                error_type=ErrorType.AUTHENTICATION_ERROR,
                status_code=401,
                response_data={"detail": "Authentication credentials were not provided."},
                exception_class=None,
                exception_message=None,
                expected_in_result=["authentication", "credentials", "not provided"],
                description="API authentication failure"
            ),
            
            ErrorType.FORBIDDEN_ERROR: ErrorScenario(
                error_type=ErrorType.FORBIDDEN_ERROR,
                status_code=403,
                response_data={"detail": "You do not have permission to perform this action."},
                exception_class=None,
                exception_message=None,
                expected_in_result=["permission", "forbidden", "access"],
                description="API permission denied"
            ),
            
            ErrorType.NOT_FOUND_ERROR: ErrorScenario(
                error_type=ErrorType.NOT_FOUND_ERROR,
                status_code=404,
                response_data={"detail": "Not found."},
                exception_class=None,
                exception_message=None,
                expected_in_result=["not found", "does not exist", "no results"],
                description="Resource not found"
            ),
            
            ErrorType.RATE_LIMIT_ERROR: ErrorScenario(
                error_type=ErrorType.RATE_LIMIT_ERROR,
                status_code=429,
                response_data={"detail": "Request was throttled. Expected available in 3600 seconds."},
                exception_class=None,
                exception_message=None,
                expected_in_result=["throttled", "expected available", "seconds"],
                description="API rate limit exceeded"
            ),
            
            ErrorType.SERVER_ERROR: ErrorScenario(
                error_type=ErrorType.SERVER_ERROR,
                status_code=500,
                response_data=None,
                exception_class=None,
                exception_message=None,
                expected_in_result=["server error", "internal error", "error occurred"],
                description="Internal server error"
            ),
            
            ErrorType.BAD_GATEWAY: ErrorScenario(
                error_type=ErrorType.BAD_GATEWAY,
                status_code=502,
                response_data={"error": "Bad Gateway"},
                exception_class=None,
                exception_message=None,
                expected_in_result=["gateway", "proxy", "server error"],
                description="Bad gateway error"
            ),
            
            ErrorType.SERVICE_UNAVAILABLE: ErrorScenario(
                error_type=ErrorType.SERVICE_UNAVAILABLE,
                status_code=503,
                response_data={"error": "Service Temporarily Unavailable"},
                exception_class=None,
                exception_message=None,
                expected_in_result=["unavailable", "maintenance", "temporarily"],
                description="Service unavailable"
            ),
            
            ErrorType.GATEWAY_TIMEOUT: ErrorScenario(
                error_type=ErrorType.GATEWAY_TIMEOUT,
                status_code=504,
                response_data={"error": "Gateway Timeout"},
                exception_class=None,
                exception_message=None,
                expected_in_result=["timeout", "gateway", "slow"],
                description="Gateway timeout"
            ),
            
            ErrorType.NETWORK_TIMEOUT: ErrorScenario(
                error_type=ErrorType.NETWORK_TIMEOUT,
                status_code=None,
                response_data=None,
                exception_class=httpx.TimeoutException,
                exception_message="Request timeout after 30 seconds",
                expected_in_result=["timeout", "network", "slow"],
                description="Network request timeout"
            ),
            
            ErrorType.CONNECTION_ERROR: ErrorScenario(
                error_type=ErrorType.CONNECTION_ERROR,
                status_code=None,
                response_data=None,
                exception_class=httpx.ConnectError,
                exception_message="Failed to establish connection",
                expected_in_result=["connection", "network", "failed"],
                description="Network connection failure"
            ),
            
            ErrorType.SSL_ERROR: ErrorScenario(
                error_type=ErrorType.SSL_ERROR,
                status_code=None,
                response_data=None,
                exception_class=httpx.ConnectError,
                exception_message="SSL certificate verification failed",
                expected_in_result=["ssl", "certificate", "security"],
                description="SSL/TLS connection error"
            ),
            
            ErrorType.DNS_ERROR: ErrorScenario(
                error_type=ErrorType.DNS_ERROR,
                status_code=None,
                response_data=None,
                exception_class=httpx.ConnectError,
                exception_message="Name or service not known",
                expected_in_result=["dns", "hostname", "resolve"],
                description="DNS resolution failure"
            ),
            
            ErrorType.MALFORMED_JSON: ErrorScenario(
                error_type=ErrorType.MALFORMED_JSON,
                status_code=200,
                response_data=None,
                exception_class=ValueError,
                exception_message="Invalid JSON response",
                expected_in_result=["json", "parse", "invalid", "malformed"],
                description="Malformed JSON response"
            ),
            
            ErrorType.EMPTY_RESPONSE: ErrorScenario(
                error_type=ErrorType.EMPTY_RESPONSE,
                status_code=200,
                response_data={"count": 0, "results": []},
                exception_class=None,
                exception_message=None,
                expected_in_result=["no", "empty", "not found", "no results"],
                description="Empty API response"
            ),
            
            ErrorType.INVALID_CONTENT_TYPE: ErrorScenario(
                error_type=ErrorType.INVALID_CONTENT_TYPE,
                status_code=200,
                response_data=None,
                exception_class=None,
                exception_message=None,
                expected_in_result=["content", "format", "invalid"],
                description="Invalid content type response"
            )
        }
    
    async def test_error_scenario(
        self, 
        tool_name: str, 
        mcp_server: Any, 
        error_type: ErrorType,
        test_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test a specific error scenario for a tool."""
        scenario = self.error_scenarios[error_type]
        test_params = test_params or {}
        
        logger.info(f"Testing {tool_name} - {scenario.description}")
        
        with patch('httpx.AsyncClient.get') as mock_get, \
             patch('httpx.AsyncClient.post') as mock_post:
            
            # Configure mock based on scenario
            if scenario.exception_class:
                # Test network/connection exceptions
                mock_get.side_effect = scenario.exception_class(scenario.exception_message)
                mock_post.side_effect = scenario.exception_class(scenario.exception_message)
            else:
                # Test HTTP response scenarios
                mock_response = MagicMock()
                mock_response.status_code = scenario.status_code
                
                if scenario.error_type == ErrorType.MALFORMED_JSON:
                    mock_response.json.side_effect = ValueError("Invalid JSON")
                    mock_response.text = "Invalid JSON response"
                elif scenario.error_type == ErrorType.INVALID_CONTENT_TYPE:
                    mock_response.json.side_effect = ValueError("Invalid content type")
                    mock_response.text = "<html>Not JSON</html>"
                    mock_response.headers = {"content-type": "text/html"}
                elif scenario.response_data:
                    mock_response.json.return_value = scenario.response_data
                else:
                    mock_response.text = f"HTTP {scenario.status_code} Error"
                
                mock_get.return_value = mock_response
                mock_post.return_value = mock_response
            
            try:
                # Execute the tool
                result = await mcp_server.get_tool(tool_name).call(**test_params)
                
                # Validate the result
                result_lower = result.lower()
                found_expected = any(expected.lower() in result_lower 
                                   for expected in scenario.expected_in_result)
                
                return {
                    "tool_name": tool_name,
                    "error_type": error_type.value,
                    "scenario_description": scenario.description,
                    "success": True,
                    "result_length": len(result),
                    "found_expected_content": found_expected,
                    "expected_terms": scenario.expected_in_result,
                    "actual_result_snippet": result[:200] + "..." if len(result) > 200 else result,
                    "error": None
                }
                
            except Exception as e:
                logger.error(f"Unexpected exception in {tool_name} - {scenario.description}: {e}")
                return {
                    "tool_name": tool_name,
                    "error_type": error_type.value,
                    "scenario_description": scenario.description,
                    "success": False,
                    "error": str(e),
                    "exception_type": type(e).__name__
                }
    
    async def test_all_error_scenarios(
        self, 
        tool_name: str, 
        mcp_server: Any,
        test_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Test all error scenarios for a specific tool."""
        results = []
        
        logger.info(f"🧪 Testing all error scenarios for {tool_name}")
        
        for error_type in self.error_scenarios.keys():
            try:
                result = await self.test_error_scenario(tool_name, mcp_server, error_type, test_params)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to test {error_type.value} for {tool_name}: {e}")
                results.append({
                    "tool_name": tool_name,
                    "error_type": error_type.value,
                    "success": False,
                    "error": f"Test framework error: {str(e)}"
                })
        
        # Summary
        successful_tests = sum(1 for r in results if r.get("success", False))
        logger.info(f"✅ {successful_tests}/{len(results)} error scenarios passed for {tool_name}")
        
        return results
    
    def generate_error_test_report(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """Generate a comprehensive error testing report."""
        total_tests = sum(len(tool_results) for tool_results in all_results)
        total_successful = sum(
            sum(1 for test in tool_results if test.get("success", False))
            for tool_results in all_results
        )
        
        report = f"""
# CourtListener MCP Server - Error Handling Test Report

## Summary
- **Total Error Tests**: {total_tests}
- **Successful Tests**: {total_successful}
- **Success Rate**: {(total_successful/total_tests)*100:.1f}%

## Test Results by Tool

"""
        
        for tool_results in all_results:
            if not tool_results:
                continue
                
            tool_name = tool_results[0]["tool_name"]
            tool_successful = sum(1 for test in tool_results if test.get("success", False))
            
            report += f"### {tool_name}\n"
            report += f"- **Tests**: {len(tool_results)}\n"
            report += f"- **Passed**: {tool_successful}\n"
            report += f"- **Success Rate**: {(tool_successful/len(tool_results))*100:.1f}%\n\n"
            
            # Add failed tests details
            failed_tests = [test for test in tool_results if not test.get("success", False)]
            if failed_tests:
                report += "**Failed Tests:**\n"
                for test in failed_tests:
                    report += f"- {test['error_type']}: {test.get('error', 'Unknown error')}\n"
                report += "\n"
        
        return report


# Convenience functions for common error testing patterns
async def test_tool_authentication_errors(tool_name: str, mcp_server: Any) -> Dict[str, Any]:
    """Quick test for authentication-related errors."""
    framework = ErrorTestFramework()
    auth_errors = [
        ErrorType.AUTHENTICATION_ERROR,
        ErrorType.FORBIDDEN_ERROR
    ]
    
    results = []
    for error_type in auth_errors:
        result = await framework.test_error_scenario(tool_name, mcp_server, error_type)
        results.append(result)
    
    return results


async def test_tool_network_errors(tool_name: str, mcp_server: Any) -> Dict[str, Any]:
    """Quick test for network-related errors."""
    framework = ErrorTestFramework()
    network_errors = [
        ErrorType.NETWORK_TIMEOUT,
        ErrorType.CONNECTION_ERROR,
        ErrorType.SSL_ERROR,
        ErrorType.DNS_ERROR
    ]
    
    results = []
    for error_type in network_errors:
        result = await framework.test_error_scenario(tool_name, mcp_server, error_type)
        results.append(result)
    
    return results


async def test_tool_http_errors(tool_name: str, mcp_server: Any) -> Dict[str, Any]:
    """Quick test for HTTP status code errors."""
    framework = ErrorTestFramework()
    http_errors = [
        ErrorType.NOT_FOUND_ERROR,
        ErrorType.RATE_LIMIT_ERROR,
        ErrorType.SERVER_ERROR,
        ErrorType.BAD_GATEWAY,
        ErrorType.SERVICE_UNAVAILABLE,
        ErrorType.GATEWAY_TIMEOUT
    ]
    
    results = []
    for error_type in http_errors:
        result = await framework.test_error_scenario(tool_name, mcp_server, error_type)
        results.append(result)
    
    return results 