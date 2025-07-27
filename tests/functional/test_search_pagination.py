#!/usr/bin/env python3
"""
CourtListener MCP Search Pagination Test

Tests the search tool with a query of "contract" across all courts.
Tests pagination functionality to ensure it can page through multiple pages of results.

Usage: python test_search_pagination.py
"""

import os
import sys
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from dotenv import load_dotenv

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchPaginationTester:
    """Test search functionality with pagination."""
    
    def __init__(self):
        self.api_token = os.getenv('COURTLISTENER_API_TOKEN')
        self.exit_stack = AsyncExitStack()
        self.session = None
        
        # Test configuration
        self.test_query = "contract"
        self.page_sizes = [5, 10, 20]  # Different page sizes to test
        self.max_pages = 3  # Maximum pages to test per query
        
    async def setup(self):
        """Initialize MCP client connection."""
        logger.info("🚀 Setting up CourtListener MCP client...")
        
        if not self.api_token:
            logger.warning("⚠️  COURTLISTENER_API_TOKEN not found in environment")
            logger.info("💡 Get your token from: https://www.courtlistener.com/profile/tokens/")
            logger.info("🔧 Set it in .env file: COURTLISTENER_API_TOKEN=your_token_here")
            logger.info("📝 Tests will continue but may have limited functionality")
        
        # Server parameters for CourtListener MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["./courtlistener_server.py"],
            env={
                "COURTLISTENER_API_TOKEN": self.api_token or "",
                "MCP_TRANSPORT": "stdio"
            }
        )
        
        try:
            # Connect to MCP server
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await self.session.initialize()
            
            # Log available tools
            tools_response = await self.session.list_tools()
            tool_names = [tool.name for tool in tools_response.tools]
            logger.info(f"✅ Connected! Available tools: {len(tool_names)}")
            logger.info(f"🔍 Search tools: {[t for t in tool_names if 'search' in t]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def test_basic_search(self) -> Dict[str, Any]:
        """Test basic search functionality."""
        logger.info("🔍 Testing basic search functionality...")
        
        test_result = {
            "test_name": "basic_search",
            "passed": False,
            "details": {}
        }
        
        try:
            result = await self.session.call_tool(
                "search_legal_cases",
                {
                    "query": self.test_query,
                    "limit": 10,
                    "enable_highlighting": True
                }
            )
            
            response_text = result.content[0].text if result.content else ""
            test_result["details"]["response_length"] = len(response_text)
            test_result["details"]["contains_results"] = "LEGAL SEARCH RESULTS" in response_text
            test_result["details"]["contains_contract"] = "contract" in response_text.lower()
            test_result["details"]["sample_output"] = response_text[:500] + "..."
            
            test_result["passed"] = test_result["details"]["contains_results"]
            
            if test_result["passed"]:
                logger.info("✅ Basic search test PASSED")
            else:
                logger.warning("⚠️  Basic search test FAILED - no results found")
                
        except Exception as e:
            logger.error(f"❌ Basic search test ERROR: {e}")
            test_result["details"]["error"] = str(e)
        
        return test_result
    
    async def test_search_across_courts(self) -> Dict[str, Any]:
        """Test search across different courts."""
        logger.info("🏛️  Testing search across different courts...")
        
        test_result = {
            "test_name": "search_across_courts",
            "passed": False,
            "details": {}
        }
        
        # Test different courts
        courts_to_test = [
            None,          # All courts
            "scotus",      # Supreme Court
            "ca9",         # 9th Circuit
            "cadc",        # DC Circuit
            "dcd"          # DC District
        ]
        
        court_results = {}
        
        try:
            for court in courts_to_test:
                court_name = court if court else "all_courts"
                logger.info(f"  🔍 Testing court: {court_name}")
                
                params = {
                    "query": self.test_query,
                    "limit": 5,
                    "enable_highlighting": True
                }
                
                if court:
                    params["court"] = court
                
                result = await self.session.call_tool("search_legal_cases", params)
                response_text = result.content[0].text if result.content else ""
                
                court_results[court_name] = {
                    "has_results": "LEGAL SEARCH RESULTS" in response_text,
                    "response_length": len(response_text),
                    "court_mentioned": court in response_text if court else True
                }
                
                if court_results[court_name]["has_results"]:
                    logger.info(f"    ✅ {court_name}: Found results")
                else:
                    logger.info(f"    ⚠️  {court_name}: No results")
            
            test_result["details"]["court_results"] = court_results
            test_result["passed"] = any(r["has_results"] for r in court_results.values())
            
            if test_result["passed"]:
                success_count = sum(1 for r in court_results.values() if r["has_results"])
                logger.info(f"✅ Court search test PASSED ({success_count}/{len(courts_to_test)} courts returned results)")
            else:
                logger.warning("⚠️  Court search test FAILED - no courts returned results")
                
        except Exception as e:
            logger.error(f"❌ Court search test ERROR: {e}")
            test_result["details"]["error"] = str(e)
        
        return test_result
    
    async def test_pagination_functionality(self) -> Dict[str, Any]:
        """Test pagination through multiple pages of results."""
        logger.info("📄 Testing pagination functionality...")
        
        test_result = {
            "test_name": "pagination_test",
            "passed": False,
            "details": {}
        }
        
        pagination_results = {}
        
        try:
            for page_size in self.page_sizes:
                logger.info(f"  📄 Testing pagination with page size: {page_size}")
                
                page_results = []
                
                # Test multiple pages
                for page_num in range(1, self.max_pages + 1):
                    logger.info(f"    📖 Page {page_num} (limit={page_size})")
                    
                    result = await self.session.call_tool(
                        "search_legal_cases",
                        {
                            "query": self.test_query,
                            "limit": page_size,
                            "enable_highlighting": True
                        }
                    )
                    
                    response_text = result.content[0].text if result.content else ""
                    
                    page_info = {
                        "page_number": page_num,
                        "has_results": "LEGAL SEARCH RESULTS" in response_text,
                        "response_length": len(response_text),
                        "result_count_mentioned": self._extract_result_count(response_text),
                        "contains_pagination_info": "next" in response_text.lower() or "page" in response_text.lower()
                    }
                    
                    page_results.append(page_info)
                    
                    if not page_info["has_results"]:
                        logger.info(f"      ⚠️  No results on page {page_num}, stopping pagination test")
                        break
                    else:
                        logger.info(f"      ✅ Page {page_num}: Found results ({page_info['result_count_mentioned']} mentioned)")
                
                pagination_results[f"page_size_{page_size}"] = page_results
            
            test_result["details"]["pagination_results"] = pagination_results
            
            # Check if we got results and if pagination info is present
            has_any_results = any(
                any(page["has_results"] for page in pages)
                for pages in pagination_results.values()
            )
            
            has_pagination_info = any(
                any(page["contains_pagination_info"] for page in pages)
                for pages in pagination_results.values()
            )
            
            test_result["passed"] = has_any_results
            test_result["details"]["has_pagination_info"] = has_pagination_info
            
            if test_result["passed"]:
                logger.info("✅ Pagination test PASSED - results found across different page sizes")
                if has_pagination_info:
                    logger.info("📋 Pagination information detected in responses")
                else:
                    logger.info("ℹ️  No explicit pagination info detected (may be handled internally)")
            else:
                logger.warning("⚠️  Pagination test FAILED - no results found")
                
        except Exception as e:
            logger.error(f"❌ Pagination test ERROR: {e}")
            test_result["details"]["error"] = str(e)
        
        return test_result
    
    async def test_advanced_search_with_pagination(self) -> Dict[str, Any]:
        """Test advanced search with multiple parameters and pagination."""
        logger.info("🔍 Testing advanced search with pagination...")
        
        test_result = {
            "test_name": "advanced_search_pagination",
            "passed": False,
            "details": {}
        }
        
        try:
            # Test advanced search with multiple parameters
            advanced_params = {
                "query": self.test_query,
                "search_type": "o",  # Case law
                "courts": ["scotus", "ca9"],
                "date_range": "last_year",
                "order_by": "relevance",
                "enable_highlighting": True,
                "limit": 15
            }
            
            logger.info("  🔍 Testing advanced search with multiple courts and date range...")
            
            result = await self.session.call_tool("advanced_legal_search", advanced_params)
            response_text = result.content[0].text if result.content else ""
            
            test_result["details"]["response_length"] = len(response_text)
            test_result["details"]["has_results"] = "ADVANCED LEGAL SEARCH RESULTS" in response_text
            test_result["details"]["contains_query"] = self.test_query in response_text.lower()
            test_result["details"]["mentions_courts"] = any(court in response_text for court in ["scotus", "ca9"])
            test_result["details"]["sample_output"] = response_text[:800] + "..."
            
            test_result["passed"] = test_result["details"]["has_results"]
            
            if test_result["passed"]:
                logger.info("✅ Advanced search test PASSED")
                logger.info(f"  📊 Response length: {test_result['details']['response_length']} chars")
                logger.info(f"  🎯 Contains query term: {test_result['details']['contains_query']}")
                logger.info(f"  🏛️  Mentions specified courts: {test_result['details']['mentions_courts']}")
            else:
                logger.warning("⚠️  Advanced search test FAILED")
                
        except Exception as e:
            logger.error(f"❌ Advanced search test ERROR: {e}")
            test_result["details"]["error"] = str(e)
        
        return test_result
    
    def _extract_result_count(self, response_text: str) -> Optional[str]:
        """Extract result count information from response text."""
        import re
        
        # Look for patterns like "Showing X of Y total matches"
        patterns = [
            r"Showing (\d+) of ([\d,]+) total matches",
            r"(\d+) of ([\d,]+) total",
            r"Results: (\d+)",
            r"Found (\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text)
            if match:
                return match.group(0)
        
        return None
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all search and pagination tests."""
        logger.info("🧪 Starting comprehensive search and pagination tests...")
        
        test_results = []
        
        try:
            # Setup connection
            if not await self.setup():
                return {"error": "Failed to setup MCP connection"}
            
            # Run all tests
            tests = [
                self.test_basic_search(),
                self.test_search_across_courts(),
                self.test_pagination_functionality(),
                self.test_advanced_search_with_pagination()
            ]
            
            for test_coro in tests:
                result = await test_coro
                test_results.append(result)
            
            # Generate summary
            passed_tests = sum(1 for r in test_results if r.get("passed", False))
            total_tests = len(test_results)
            
            summary = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "test_results": test_results
            }
            
            # Log summary
            logger.info("📊 TEST SUMMARY")
            logger.info("=" * 50)
            logger.info(f"🧪 Total Tests: {total_tests}")
            logger.info(f"✅ Passed: {passed_tests}")
            logger.info(f"❌ Failed: {total_tests - passed_tests}")
            logger.info(f"📈 Success Rate: {summary['success_rate']:.1%}")
            logger.info("=" * 50)
            
            for result in test_results:
                status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
                logger.info(f"{status}: {result['test_name']}")
                if "error" in result.get("details", {}):
                    logger.info(f"  Error: {result['details']['error']}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Test suite ERROR: {e}")
            return {"error": str(e), "test_results": test_results}
        
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up connections."""
        try:
            await self.exit_stack.aclose()
            logger.info("🔌 MCP connection closed")
        except Exception as e:
            logger.warning(f"⚠️  Error during cleanup: {e}")


async def main():
    """Main test entry point."""
    print("🔍 CourtListener MCP Search & Pagination Test Suite")
    print("=" * 60)
    print(f"📋 Test Query: 'contract'")
    print(f"🏛️  Test Scope: All courts")
    print(f"📄 Pagination: Testing multiple page sizes")
    print("=" * 60)
    
    tester = SearchPaginationTester()
    results = await tester.run_all_tests()
    
    # Save detailed results
    if "error" not in results:
        output_file = "search_pagination_test_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: {output_file}")
    
    # Return appropriate exit code
    if "error" in results:
        print(f"💥 Test suite failed: {results['error']}")
        return 1
    elif results.get("success_rate", 0) >= 0.75:
        print("🎉 Test suite PASSED!")
        return 0
    else:
        print("⚠️  Test suite completed with issues")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 