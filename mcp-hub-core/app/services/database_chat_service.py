"""
Database Chat Service - Integrates multiple databases with chat functionality
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime

from app.core.multi_database_manager import multi_db_manager, QueryResult
from app.services.llm_manager import llm_manager

logger = logging.getLogger(__name__)

class DatabaseChatService:
    """Service for integrating database queries with chat functionality"""
    
    def __init__(self):
        self.db_manager = multi_db_manager
        self.llm_manager = llm_manager
    
    async def process_database_query(self, user_message: str) -> Dict[str, Any]:
        """Process user message and execute database queries"""
        try:
            # Analyze the user message to determine intent
            intent = await self._analyze_query_intent(user_message)
            
            if intent['type'] == 'schema_inquiry':
                return await self._handle_schema_inquiry(intent)
            elif intent['type'] == 'data_query':
                return await self._handle_data_query(intent, user_message)
            elif intent['type'] == 'search':
                return await self._handle_search_query(intent, user_message)
            elif intent['type'] == 'health_check':
                return await self._handle_health_check(intent)
            else:
                return await self._handle_general_database_question(intent, user_message)
                
        except Exception as e:
            logger.error(f"Failed to process database query: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "I encountered an error while processing your database query."
            }
    
    async def _analyze_query_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message to determine database query intent"""
        message_lower = message.lower()
        
        # Schema-related keywords
        schema_keywords = ['schema', 'structure', 'tables', 'columns', 'describe', 'show tables']
        if any(keyword in message_lower for keyword in schema_keywords):
            return {
                'type': 'schema_inquiry',
                'database_specific': self._extract_database_name(message),
                'intent': 'schema'
            }
        
        # Data query keywords
        query_keywords = ['select', 'query', 'get', 'find', 'show', 'list', 'count', 'sum', 'avg']
        if any(keyword in message_lower for keyword in query_keywords):
            return {
                'type': 'data_query',
                'database_specific': self._extract_database_name(message),
                'intent': 'data_query'
            }
        
        # Search keywords
        search_keywords = ['search', 'look for', 'find', 'contains', 'like']
        if any(keyword in message_lower for keyword in search_keywords):
            return {
                'type': 'search',
                'database_specific': self._extract_database_name(message),
                'intent': 'search'
            }
        
        # Health check keywords
        health_keywords = ['status', 'health', 'connection', 'ping', 'alive']
        if any(keyword in message_lower for keyword in health_keywords):
            return {
                'type': 'health_check',
                'database_specific': self._extract_database_name(message),
                'intent': 'health'
            }
        
        # General database question
        return {
            'type': 'general',
            'database_specific': self._extract_database_name(message),
            'intent': 'general'
        }
    
    def _extract_database_name(self, message: str) -> Optional[str]:
        """Extract database name from message"""
        # Look for patterns like "in database X", "from database Y", etc.
        patterns = [
            r'in database (\w+)',
            r'from database (\w+)',
            r'database (\w+)',
            r'(\w+) database'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def _handle_schema_inquiry(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schema-related queries"""
        try:
            if intent['database_specific']:
                # Get schema for specific database
                schema = await self.db_manager.get_database_schema(intent['database_specific'])
                response = await self._format_schema_response(schema)
            else:
                # Get schemas for all databases
                schemas = await self.db_manager.get_all_schemas()
                response = await self._format_all_schemas_response(schemas)
            
            return {
                'success': True,
                'response': response,
                'data': schema if intent['database_specific'] else schemas
            }
            
        except Exception as e:
            logger.error(f"Schema inquiry failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"I couldn't retrieve the schema information: {str(e)}"
            }
    
    async def _handle_data_query(self, intent: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle data query requests"""
        try:
            # Generate SQL query using LLM
            sql_query = await self._generate_sql_query(user_message, intent['database_specific'])
            
            if not sql_query:
                return {
                    'success': False,
                    'response': "I couldn't understand your query. Please try rephrasing it."
                }
            
            # Execute query
            if intent['database_specific']:
                result = await self.db_manager.execute_query(intent['database_specific'], sql_query)
                response = await self._format_query_response(result)
            else:
                results = await self.db_manager.execute_query_all_databases(sql_query)
                response = await self._format_multi_database_response(results)
            
            return {
                'success': True,
                'response': response,
                'query': sql_query,
                'data': result if intent['database_specific'] else results
            }
            
        except Exception as e:
            logger.error(f"Data query failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"I couldn't execute your query: {str(e)}"
            }
    
    async def _handle_search_query(self, intent: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle search queries across databases"""
        try:
            # Extract search term
            search_term = self._extract_search_term(user_message)
            
            # Search across all databases
            results = await self.db_manager.search_across_databases(search_term)
            
            response = await self._format_search_response(results, search_term)
            
            return {
                'success': True,
                'response': response,
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"I couldn't perform the search: {str(e)}"
            }
    
    async def _handle_health_check(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database health check requests"""
        try:
            if intent['database_specific']:
                # Check specific database
                result = await self.db_manager.execute_query(intent['database_specific'], "SELECT 1 as health_check")
                response = f"Database '{intent['database_specific']}' is {'healthy' if result.success else 'unhealthy'}"
            else:
                # Check all databases
                databases = self.db_manager.get_database_list()
                health_status = []
                
                for db in databases:
                    if db['is_active']:
                        result = await self.db_manager.execute_query(db['name'], "SELECT 1 as health_check")
                        health_status.append({
                            'database': db['name'],
                            'status': 'healthy' if result.success else 'unhealthy',
                            'response_time': result.execution_time
                        })
                
                response = await self._format_health_response(health_status)
            
            return {
                'success': True,
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"I couldn't check database health: {str(e)}"
            }
    
    async def _handle_general_database_question(self, intent: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle general database questions"""
        try:
            # Get available databases
            databases = self.db_manager.get_database_list()
            
            # Use LLM to generate response
            context = f"Available databases: {[db['name'] for db in databases]}"
            response = await self.llm_manager.generate_response(
                f"{context}\n\nUser question: {user_message}"
            )
            
            return {
                'success': True,
                'response': response,
                'databases': databases
            }
            
        except Exception as e:
            logger.error(f"General database question failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"I couldn't process your question: {str(e)}"
            }
    
    async def _generate_sql_query(self, user_message: str, database_name: Optional[str] = None) -> Optional[str]:
        """Generate SQL query from natural language"""
        try:
            # Get schema information for context
            schema_context = ""
            if database_name:
                schema = await self.db_manager.get_database_schema(database_name)
                schema_context = f"Database schema: {json.dumps(schema, indent=2)}"
            else:
                schemas = await self.db_manager.get_all_schemas()
                schema_context = f"Available databases and schemas: {json.dumps(schemas, indent=2)}"
            
            # Create prompt for LLM
            prompt = f"""
            Convert the following natural language request to SQL:
            
            User request: {user_message}
            
            {schema_context}
            
            Return only the SQL query, no explanations.
            """
            
            response = await self.llm_manager.generate_response(prompt)
            
            # Extract SQL query from response
            sql_query = self._extract_sql_from_response(response)
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return None
    
    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """Extract SQL query from LLM response"""
        # Look for SQL patterns
        sql_patterns = [
            r'SELECT.*?;',
            r'INSERT.*?;',
            r'UPDATE.*?;',
            r'DELETE.*?;',
            r'CREATE.*?;',
            r'DROP.*?;'
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_search_term(self, message: str) -> str:
        """Extract search term from message"""
        # Remove common search keywords
        keywords_to_remove = ['search for', 'find', 'look for', 'show me']
        
        search_term = message
        for keyword in keywords_to_remove:
            search_term = re.sub(keyword, '', search_term, flags=re.IGNORECASE)
        
        return search_term.strip()
    
    async def _format_schema_response(self, schema: Dict[str, Any]) -> str:
        """Format schema response for user"""
        if not schema.get('success', False):
            return f"Could not retrieve schema: {schema.get('error', 'Unknown error')}"
        
        response = f"**Database Schema for {schema['database_name']}:**\n\n"
        
        if schema['type'] == 'postgresql':
            # Group by table
            tables = {}
            for column in schema.get('tables', []):
                table_name = column.get('table_name')
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(column)
            
            for table_name, columns in tables.items():
                response += f"**Table: {table_name}**\n"
                for col in columns:
                    response += f"  - {col.get('column_name')} ({col.get('data_type')})\n"
                response += "\n"
        
        elif schema['type'] == 'sqlite':
            for table in schema.get('tables', []):
                response += f"**Table: {table.get('table_name')}**\n"
                for col in table.get('columns', []):
                    response += f"  - {col.get('name')} ({col.get('type')})\n"
                response += "\n"
        
        return response
    
    async def _format_all_schemas_response(self, schemas: Dict[str, Dict[str, Any]]) -> str:
        """Format response for all database schemas"""
        response = "**Available Databases and Schemas:**\n\n"
        
        for db_name, schema in schemas.items():
            if schema.get('success', False):
                response += f"**Database: {db_name}**\n"
                response += await self._format_schema_response(schema)
                response += "\n"
            else:
                response += f"**Database: {db_name}** - Error: {schema.get('error', 'Unknown error')}\n\n"
        
        return response
    
    async def _format_query_response(self, result: QueryResult) -> str:
        """Format query result for user"""
        if not result.success:
            return f"Query failed: {result.error}"
        
        if result.row_count == 0:
            return "No results found."
        
        response = f"**Query Results ({result.row_count} rows):**\n\n"
        
        # Show first few rows
        max_rows = 10
        for i, row in enumerate(result.data[:max_rows]):
            response += f"Row {i+1}:\n"
            for key, value in row.items():
                response += f"  {key}: {value}\n"
            response += "\n"
        
        if result.row_count > max_rows:
            response += f"... and {result.row_count - max_rows} more rows\n"
        
        response += f"\n*Execution time: {result.execution_time:.3f}s*"
        
        return response
    
    async def _format_multi_database_response(self, results: Dict[str, QueryResult]) -> str:
        """Format response for multi-database query results"""
        response = "**Query Results Across Databases:**\n\n"
        
        for db_name, result in results.items():
            response += f"**Database: {db_name}**\n"
            if result.success:
                response += f"  Rows: {result.row_count}\n"
                response += f"  Execution time: {result.execution_time:.3f}s\n"
                if result.row_count > 0:
                    response += f"  Sample data: {result.data[0] if result.data else 'N/A'}\n"
            else:
                response += f"  Error: {result.error}\n"
            response += "\n"
        
        return response
    
    async def _format_search_response(self, results: Dict[str, List[Dict[str, Any]]], search_term: str) -> str:
        """Format search results for user"""
        response = f"**Search Results for '{search_term}':**\n\n"
        
        total_results = 0
        for db_name, db_results in results.items():
            if db_results:
                response += f"**Database: {db_name}**\n"
                for result in db_results:
                    response += f"  - {result}\n"
                response += "\n"
                total_results += len(db_results)
        
        if total_results == 0:
            response = f"No results found for '{search_term}' across all databases."
        
        return response
    
    async def _format_health_response(self, health_status: List[Dict[str, Any]]) -> str:
        """Format health check response"""
        response = "**Database Health Status:**\n\n"
        
        for status in health_status:
            response += f"**{status['database']}**: {status['status']}"
            if 'response_time' in status:
                response += f" ({status['response_time']:.3f}s)"
            response += "\n"
        
        return response

# Global instance
database_chat_service = DatabaseChatService()
