#!/usr/bin/env python3
"""
CourtListener MCP Server - Citation API Specific Tests

Tests for citation API specific constraints and behaviors documented in
courtlistener-api-templates/citation-lookup-api-vlatest.html

Based on API documentation findings:
- 64,000 character limit for text requests
- Special 429 response format with 'wait_until' key
- Different throttling rules for citations vs requests
- Maximum citations per request limit
- Specific citation format requirements
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from mcp.server.fastmcp import FastMCP

from tools.citation_tools import register_citation_tools


class TestCitationAPISpecific:
    """Citation API specific tests based on documented constraints."""
    
    @pytest.fixture
    async def mcp_server(self):
        """Create MCP server with citation tools registered."""
        mcp = FastMCP(name="test")
        register_citation_tools(mcp)
        return mcp
    
    @pytest.mark.unit
    async def test_text_length_limit_64k(self, mcp_server):
        """Test 64,000 character limit for text requests."""
        # Text just under limit should work
        text_under_limit = "x" * 63999
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "citations": [],
                "message": "No citations found"
            }
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('verify_citations').call(
                text=text_under_limit
            )
            
            assert mock_get.called
            assert isinstance(result, str)
    
    @pytest.mark.unit
    async def test_text_length_limit_exceeded(self, mcp_server):
        """Test text over 64,000 character limit is blocked."""
        # Text over limit should be blocked for security
        text_over_limit = "x" * 65001
        
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock a security/validation error response
            mock_get.return_value.status_code = 400
            mock_get.return_value.json.return_value = {
                "detail": "Request blocked for security. Text too long."
            }
            
            result = await mcp_server.get_tool('verify_citations').call(
                text=text_over_limit
            )
            
            assert "blocked" in result.lower() or "too long" in result.lower()
    
    @pytest.mark.unit
    async def test_citation_throttle_429_with_wait_until(self, mcp_server):
        """Test citation-specific 429 response with wait_until field."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock citation API specific 429 response
            mock_get.return_value.status_code = 429
            mock_get.return_value.json.return_value = {
                "detail": "Citation throttle exceeded",
                "wait_until": "2024-01-15T15:30:00Z"  # ISO-8601 datetime
            }
            
            result = await mcp_server.get_tool('verify_citations').call(
                text="See Brown v. Board, 347 U.S. 483 (1954)"
            )
            
            # Should mention throttling and wait time
            assert "throttle" in result.lower() or "wait" in result.lower()
            assert "15:30" in result  # Should include the wait time
    
    @pytest.mark.unit
    async def test_max_citations_per_request(self, mcp_server):
        """Test maximum citations per request limit."""
        # Create text with many citations
        many_citations = "See " + ", ".join([
            f"Case {i} v. State, {100+i} U.S. {200+i} (19{50+i%50})"
            for i in range(50)  # Many citations
        ])
        
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock response where some citations have status 429 
            mock_get.return_value.json.return_value = {
                "citations": [
                    {"citation": "100 U.S. 200", "status": 200, "found": True},
                    {"citation": "101 U.S. 201", "status": 200, "found": True},
                    # ... first several work
                    {"citation": "149 U.S. 249", "status": 429, "message": "Too many citations requested"}
                ]
            }
            mock_get.return_value.status_code = 200
            
            result = await mcp_server.get_tool('verify_citations').call(
                text=many_citations
            )
            
            # Should handle partial success gracefully
            assert "citations" in result.lower()
            # May mention some were not processed
    
    @pytest.mark.unit
    async def test_citation_format_requirements(self, mcp_server):
        """Test citation format requirements from API docs."""
        test_cases = [
            # Valid citations that should be processed
            ("347 U.S. 483", True),
            ("576 U.S. 644", True),
            ("123 F.3d 456", True),
            
            # Invalid citations that won't be matched
            ("22 U.S. ___", False),  # No page number
            ("U.S. 123", False),     # No volume number
            ("Random text", False),   # Not a citation
        ]
        
        for citation_text, should_process in test_cases:
            with patch('httpx.AsyncClient.get') as mock_get:
                if should_process:
                    mock_get.return_value.json.return_value = {
                        "citations": [{
                            "citation": citation_text,
                            "status": 200,
                            "found": True
                        }]
                    }
                else:
                    mock_get.return_value.json.return_value = {
                        "citations": [{
                            "citation": citation_text,
                            "status": 400,
                            "message": "Invalid citation format"
                        }]
                    }
                mock_get.return_value.status_code = 200
                
                result = await mcp_server.get_tool('verify_citations').call(
                    text=f"See {citation_text}"
                )
                
                assert isinstance(result, str)
                if should_process:
                    assert citation_text in result
    
    @pytest.mark.unit
    async def test_citation_api_same_auth_as_other_apis(self, mcp_server):
        """Test citation API uses same authentication as other APIs."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Test 401 response matches other APIs
            mock_get.return_value.status_code = 401
            mock_get.return_value.json.return_value = {
                "detail": "Authentication credentials were not provided."
            }
            
            result = await mcp_server.get_tool('verify_citations').call(
                text="347 U.S. 483"
            )
            
            # Should use same error format as other CourtListener APIs
            assert "authentication" in result.lower()
            assert "credentials" in result.lower()
    
    @pytest.mark.unit
    async def test_citation_api_general_throttle(self, mcp_server):
        """Test citation API general request throttle (separate from citation throttle)."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Test general API throttle (not citation-specific)
            mock_get.return_value.status_code = 429
            mock_get.return_value.json.return_value = {
                "detail": "Request was throttled. Expected available in 3600 seconds."
            }
            
            result = await mcp_server.get_tool('verify_citations').call(
                text="Text with no citations"
            )
            
            # Should handle general throttling like other APIs
            assert "throttl" in result.lower()
            assert "3600" in result  # Should include the wait time
    
    @pytest.mark.unit
    async def test_unsupported_citation_types(self, mcp_server):
        """Test citations that API doesn't support (statutes, journals, etc.)."""
        unsupported_citations = [
            "42 U.S.C. § 1983",  # Statute
            "15 Harvard L. Rev. 123",  # Law journal  
            "Smith, supra note 15",  # Supra citation
            "Id. at 45"  # Id citation
        ]
        
        for citation in unsupported_citations:
            with patch('httpx.AsyncClient.get') as mock_get:
                mock_get.return_value.json.return_value = {
                    "citations": [{
                        "citation": citation,
                        "status": 400,
                        "message": "Unsupported citation type"
                    }]
                }
                mock_get.return_value.status_code = 200
                
                result = await mcp_server.get_tool('verify_citations').call(
                    text=f"See {citation}"
                )
                
                # Should handle unsupported types gracefully
                assert isinstance(result, str)
                # May indicate citation was found but not processed 