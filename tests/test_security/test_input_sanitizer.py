"""
Tests for input sanitization.
"""

import pytest
from mcp_hub.security.input_sanitizer import InputSanitizer

class TestInputSanitizer:
    """Test input sanitization functionality."""
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        sanitizer = InputSanitizer()
        
        # Test basic sanitization
        input_str = "Hello World"
        result = sanitizer.sanitize_string(input_str)
        assert result == "Hello World"
        
        # Test XSS prevention
        xss_input = "<script>alert('xss')</script>"
        result = sanitizer.sanitize_string(xss_input)
        assert "<script>" not in result
        
        # Test SQL injection prevention
        sql_input = "'; DROP TABLE users; --"
        result = sanitizer.sanitize_string(sql_input)
        assert "DROP TABLE" not in result
    
    def test_validate_query(self):
        """Test query validation."""
        sanitizer = InputSanitizer()
        
        # Valid query
        valid_query = "What is the weather today?"
        assert sanitizer.validate_query(valid_query) == True
        
        # Invalid query with SQL injection
        invalid_query = "'; DROP TABLE users; --"
        assert sanitizer.validate_query(invalid_query) == False
    
    def test_validate_username(self):
        """Test username validation."""
        sanitizer = InputSanitizer()
        
        # Valid username
        assert sanitizer.validate_username("testuser") == True
        assert sanitizer.validate_username("user123") == True
        
        # Invalid username
        assert sanitizer.validate_username("") == False
        assert sanitizer.validate_username("ab") == False  # Too short
        assert sanitizer.validate_username("user@domain") == False  # Invalid chars
