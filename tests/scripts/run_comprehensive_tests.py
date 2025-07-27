#!/usr/bin/env python3
"""
CourtListener MCP Server - Comprehensive Test Runner

Executes all CRITICAL test scenarios including:
1. Unit tests for all 17 tools
2. Comprehensive error handling tests
3. Parameter validation testing
4. Security vulnerability testing

Usage: python tests/scripts/run_comprehensive_tests.py [--tool TOOL_NAME] [--all]
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from server_factory import create_courtlistener_server, get_registered_tools
from tests.utils.error_test_framework import ErrorTestFramework
from tests.utils.parameter_validation_framework import ParameterValidationFramework


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveTestRunner:
    """Runs all critical test scenarios for CourtListener MCP tools."""
    
    def __init__(self):
        self.mcp_server = None
        self.error_framework = ErrorTestFramework()
        self.param_framework = ParameterValidationFramework()
        self.results = {
            "error_tests": [],
            "parameter_tests": [],
            "summary": {}
        }
        
        # Tool definitions with parameters (same as generator script)
        self.tool_definitions = {
            'get_opinion': {
                'params': ['opinion_id', 'cluster_id', 'opinion_type', 'author_name', 'include_content', 'limit'],
                'required': [],
                'module': 'tools.opinion_tools'
            },
            'get_cluster': {
                'params': ['cluster_id', 'case_name', 'court', 'date_filed_after', 'date_filed_before', 'citation', 'include_opinions', 'limit'],
                'required': [],
                'module': 'tools.cluster_tools'
            },
            'get_docket': {
                'params': ['docket_id', 'docket_number', 'case_name', 'court', 'nature_of_suit', 'include_entries', 'limit'],
                'required': [],
                'module': 'tools.docket_tools'
            },
            'get_court': {
                'params': ['court_id', 'court_name', 'jurisdiction', 'include_hierarchy', 'include_stats', 'limit'],
                'required': [],
                'module': 'tools.court_tools'
            },
            'search_legal_cases': {
                'params': ['query', 'search_type', 'court', 'judge', 'date_filed_after', 'date_filed_before', 'enable_highlighting', 'limit'],
                'required': ['query'],
                'module': 'tools.search_tools'
            },
            'advanced_legal_search': {
                'params': ['query', 'search_type', 'court', 'judge', 'citation', 'case_name', 'status', 'order_by', 'limit'],
                'required': ['query'],
                'module': 'tools.search_tools'
            },
            'get_judge': {
                'params': ['person_id', 'name_first', 'name_last', 'court_id', 'include_positions', 'include_education', 'limit'],
                'required': [],
                'module': 'tools.people_tools'
            },
            'get_political_affiliations': {
                'params': ['person_id', 'political_party', 'date_start_after', 'date_start_before', 'include_person_details', 'limit'],
                'required': [],
                'module': 'tools.political_affiliation_tools'
            },
            'get_aba_ratings': {
                'params': ['person_id', 'rating', 'year_rated_after', 'year_rated_before', 'include_person_details', 'limit'],
                'required': [],
                'module': 'tools.aba_ratings_tools'
            },
            'get_retention_events': {
                'params': ['person_id', 'position_id', 'event_type', 'date_after', 'date_before', 'include_details', 'limit'],
                'required': [],
                'module': 'tools.retention_events_tools'
            },
            'get_sources': {
                'params': ['source_id', 'name', 'date_modified_after', 'date_modified_before', 'include_stats', 'limit'],
                'required': [],
                'module': 'tools.sources_tools'
            },
            'get_educations': {
                'params': ['person_id', 'school', 'degree', 'degree_year_after', 'degree_year_before', 'include_person_details', 'limit'],
                'required': [],
                'module': 'tools.education_tools'
            },
            'verify_citations': {
                'params': ['text', 'volume', 'reporter', 'page'],
                'required': [],
                'module': 'tools.citation_tools'
            },
            'find_authorities_cited': {
                'params': ['citing_opinion_id', 'cited_opinion_id', 'depth', 'include_details', 'limit'],
                'required': [],
                'module': 'tools.opinions_cited_tools'
            },
            'find_citing_opinions': {
                'params': ['cited_opinion_id', 'citing_opinion_id', 'depth', 'include_details', 'limit'],
                'required': [],
                'module': 'tools.opinions_cited_tools'
            },
            'analyze_citation_network': {
                'params': ['opinion_id', 'max_depth', 'include_metadata', 'limit'],
                'required': ['opinion_id'],
                'module': 'tools.opinions_cited_tools'
            },
            'get_positions': {
                'params': ['position_id', 'person_id', 'court_id', 'position_type', 'how_selected', 'include_person_details', 'limit'],
                'required': [],
                'module': 'tools.position_tools'
            }
        }
    
    async def setup_mcp_server(self):
        """Initialize the MCP server for testing."""
        try:
            self.mcp_server = create_courtlistener_server()
            logger.info("✅ MCP server initialized successfully")
            
            # Verify tools are available
            available_tools = get_registered_tools(self.mcp_server)
            logger.info(f"📋 Available tools: {len(available_tools)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup MCP server: {e}")
            return False
    
    async def run_error_tests(self, tool_names: List[str]) -> List[List[Dict[str, Any]]]:
        """Run comprehensive error handling tests for specified tools."""
        logger.info("🧪 Running comprehensive error handling tests...")
        
        all_results = []
        
        for tool_name in tool_names:
            logger.info(f"Testing error scenarios for {tool_name}...")
            
            try:
                # Get base parameters for the tool
                tool_info = self.tool_definitions.get(tool_name, {})
                base_params = {}
                
                # Add required parameters with default values
                for required_param in tool_info.get('required', []):
                    if required_param == 'query':
                        base_params[required_param] = 'test query'
                    elif required_param == 'opinion_id':
                        base_params[required_param] = 12345
                
                # Run all error scenarios
                results = await self.error_framework.test_all_error_scenarios(
                    tool_name, self.mcp_server, base_params
                )
                all_results.append(results)
                
                # Log summary for this tool
                successful = sum(1 for r in results if r.get("success", False))
                logger.info(f"✅ {tool_name}: {successful}/{len(results)} error tests passed")
                
            except Exception as e:
                logger.error(f"❌ Error testing {tool_name}: {e}")
                all_results.append([{
                    "tool_name": tool_name,
                    "success": False,
                    "error": f"Test framework error: {str(e)}"
                }])
        
        self.results["error_tests"] = all_results
        return all_results
    
    async def run_parameter_validation_tests(self, tool_names: List[str]) -> List[List[Dict[str, Any]]]:
        """Run comprehensive parameter validation tests for specified tools."""
        logger.info("🔒 Running parameter validation tests...")
        
        all_results = []
        
        for tool_name in tool_names:
            logger.info(f"Testing parameter validation for {tool_name}...")
            
            try:
                tool_info = self.tool_definitions.get(tool_name, {})
                tool_params = {param: None for param in tool_info.get('params', [])}
                
                # Base parameters with safe values
                base_params = {}
                for required_param in tool_info.get('required', []):
                    if required_param == 'query':
                        base_params[required_param] = 'test'
                    elif required_param == 'opinion_id':
                        base_params[required_param] = 12345
                
                # Run parameter validation tests
                results = await self.param_framework.test_all_parameter_scenarios(
                    tool_name, self.mcp_server, tool_params, base_params
                )
                all_results.append(results)
                
                # Log summary with security focus
                successful = sum(1 for r in results if r.get("success", False))
                security_failures = sum(1 for r in results if 
                                      r.get("security_risk_level") in ["high", "critical"] 
                                      and not r.get("success", False))
                
                logger.info(f"✅ {tool_name}: {successful}/{len(results)} parameter tests passed")
                if security_failures > 0:
                    logger.warning(f"⚠️  {tool_name}: {security_failures} security issues found")
                
            except Exception as e:
                logger.error(f"❌ Parameter testing {tool_name}: {e}")
                all_results.append([{
                    "tool_name": tool_name,
                    "success": False,
                    "error": f"Test framework error: {str(e)}"
                }])
        
        self.results["parameter_tests"] = all_results
        return all_results
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive test report."""
        error_results = self.results["error_tests"]
        param_results = self.results["parameter_tests"]
        
        # Calculate totals
        total_error_tests = sum(len(tool_results) for tool_results in error_results)
        total_param_tests = sum(len(tool_results) for tool_results in param_results)
        
        successful_error_tests = sum(
            sum(1 for test in tool_results if test.get("success", False))
            for tool_results in error_results
        )
        successful_param_tests = sum(
            sum(1 for test in tool_results if test.get("success", False))
            for tool_results in param_results
        )
        
        # Security analysis
        security_failures = 0
        for tool_results in param_results:
            for test in tool_results:
                if (test.get("security_risk_level") in ["high", "critical"] 
                    and not test.get("success", False)):
                    security_failures += 1
        
        report = f"""
# CourtListener MCP Server - Comprehensive Test Report

## Executive Summary

### Test Coverage
- **Total Tools Tested**: {len(error_results)}
- **Error Handling Tests**: {total_error_tests}
- **Parameter Validation Tests**: {total_param_tests}
- **Total Tests**: {total_error_tests + total_param_tests}

### Results Summary
- **Error Tests Passed**: {successful_error_tests}/{total_error_tests} ({(successful_error_tests/max(total_error_tests,1))*100:.1f}%)
- **Parameter Tests Passed**: {successful_param_tests}/{total_param_tests} ({(successful_param_tests/max(total_param_tests,1))*100:.1f}%)
- **Overall Success Rate**: {((successful_error_tests + successful_param_tests)/(max(total_error_tests + total_param_tests,1)))*100:.1f}%

### Security Assessment
- **Security Test Failures**: {security_failures}
- **Security Risk Level**: {"🔴 HIGH" if security_failures > 0 else "🟢 LOW"}

---

## Detailed Results

"""
        
        # Add error handling report
        error_report = self.error_framework.generate_error_test_report(error_results)
        report += error_report
        
        # Add parameter validation report
        param_report = self.param_framework.generate_parameter_validation_report(param_results)
        report += param_report
        
        return report
    
    async def run_comprehensive_tests(self, tool_names: List[str]) -> Dict[str, Any]:
        """Run all comprehensive tests for specified tools."""
        start_time = time.time()
        
        logger.info(f"🚀 Starting comprehensive testing for {len(tool_names)} tools")
        logger.info(f"📋 Tools to test: {', '.join(tool_names)}")
        
        # Setup
        if not await self.setup_mcp_server():
            return {"success": False, "error": "Failed to setup MCP server"}
        
        try:
            # Run error handling tests
            logger.info("\n" + "="*60)
            logger.info("🔥 PHASE 1: ERROR HANDLING TESTS")
            logger.info("="*60)
            await self.run_error_tests(tool_names)
            
            # Run parameter validation tests
            logger.info("\n" + "="*60)
            logger.info("🔒 PHASE 2: PARAMETER VALIDATION TESTS")
            logger.info("="*60)
            await self.run_parameter_validation_tests(tool_names)
            
            # Generate report
            report = self.generate_comprehensive_report()
            
            # Save detailed results
            results_file = Path("tests/results/comprehensive_test_results.json")
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            # Save report
            report_file = Path("tests/results/comprehensive_test_report.md")
            with open(report_file, 'w') as f:
                f.write(report)
            
            duration = time.time() - start_time
            
            logger.info("\n" + "="*60)
            logger.info("🎉 COMPREHENSIVE TESTING COMPLETED")
            logger.info("="*60)
            logger.info(f"⏱️  Duration: {duration:.2f} seconds")
            logger.info(f"📄 Report saved: {report_file}")
            logger.info(f"📊 Results saved: {results_file}")
            
            return {
                "success": True,
                "duration": duration,
                "report_file": str(report_file),
                "results_file": str(results_file),
                "summary": self.results["summary"]
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive testing failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Main function to run comprehensive tests."""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for CourtListener MCP tools")
    parser.add_argument('--tool', help='Test specific tool only')
    parser.add_argument('--all', action='store_true', help='Test all tools')
    parser.add_argument('--quick', action='store_true', help='Quick test (subset of tools)')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.tool:
        if args.tool not in runner.tool_definitions:
            print(f"❌ Tool '{args.tool}' not found")
            print(f"Available tools: {', '.join(runner.tool_definitions.keys())}")
            return 1
        tool_names = [args.tool]
    elif args.quick:
        # Test a representative subset
        tool_names = [
            'get_opinion', 'search_legal_cases', 'get_court', 
            'verify_citations', 'get_judge'
        ]
    elif args.all:
        tool_names = list(runner.tool_definitions.keys())
    else:
        parser.print_help()
        return 1
    
    # Run comprehensive tests
    result = asyncio.run(runner.run_comprehensive_tests(tool_names))
    
    if result["success"]:
        print(f"\n✅ Comprehensive testing completed successfully!")
        print(f"📄 Report: {result['report_file']}")
        print(f"📊 Results: {result['results_file']}")
        return 0
    else:
        print(f"\n❌ Comprehensive testing failed: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 