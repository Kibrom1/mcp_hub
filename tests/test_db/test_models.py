"""
Tests for database models.
"""

import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mcp_hub.db.models import Base, MCPServer, MCPTool, MCPResource

class TestDatabaseModels:
    """Test database models."""
    
    def test_database_models_creation(self):
        """Test database model creation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name
        
        try:
            engine = create_engine(f"sqlite:///{temp_db}")
            Base.metadata.create_all(engine)
            SessionLocal = sessionmaker(bind=engine)
            
            session = SessionLocal()
            
            # Test MCPServer model
            server = MCPServer(
                name="test_server",
                uri="test_uri",
                enabled=True
            )
            session.add(server)
            session.commit()
            
            # Test MCPTool model
            tool = MCPTool(
                id="test_tool_1",
                server_name="test_server",
                name="test_tool",
                description="Test tool description",
                parameters='{"param1": "string"}'
            )
            session.add(tool)
            session.commit()
            
            # Test MCPResource model
            resource = MCPResource(
                id="test_resource_1",
                server_name="test_server",
                name="test_resource",
                uri="test://resource"
            )
            session.add(resource)
            session.commit()
            
            # Verify data was saved
            assert session.query(MCPServer).count() == 1
            assert session.query(MCPTool).count() == 1
            assert session.query(MCPResource).count() == 1
            
            session.close()
            
        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)
