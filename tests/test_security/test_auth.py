"""
Tests for authentication system.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_hub.security.auth import SecureAuthManager

class TestAuth:
    """Test authentication functionality."""
    
    def test_auth_manager_initialization(self):
        """Test auth manager initialization."""
        with patch('mcp_hub.security.auth.secure_config') as mock_config:
            mock_config.security.session_timeout = 3600
            mock_config.security.max_requests_per_minute = 60
            mock_config.security.max_login_attempts = 5
            mock_config.security.lockout_duration = 300
            
            auth_manager = SecureAuthManager()
            assert auth_manager.session_timeout == 3600
            assert auth_manager.max_requests == 60
    
    def test_password_hashing(self):
        """Test password hashing."""
        with patch('mcp_hub.security.auth.secure_config') as mock_config:
            mock_config.security.session_timeout = 3600
            mock_config.security.max_requests_per_minute = 60
            mock_config.security.max_login_attempts = 5
            mock_config.security.lockout_duration = 300
            
            auth_manager = SecureAuthManager()
            
            # Test password hashing
            password = "test_password"
            hashed = auth_manager._hash_password(password)
            assert hashed != password
            assert len(hashed) > 64  # Salt + hash length
