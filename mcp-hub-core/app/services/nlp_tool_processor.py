"""
Natural Language Tool Processor
Converts natural language queries into tool executions
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sqlite3

class NLPToolProcessor:
    """Processes natural language queries and converts them to tool executions"""
    
    def __init__(self):
        self.tool_patterns = {
            # File operations
            'list_files': [
                r'list files?',
                r'show files?',
                r'what files?',
                r'files? in',
                r'contents? of',
                r'directory',
                r'folder'
            ],
            'read_file': [
                r'read file',
                r'open file',
                r'show content',
                r'display file',
                r'view file',
                r'file content'
            ],
            'write_file': [
                r'write file',
                r'create file',
                r'save file',
                r'write to',
                r'create content'
            ],
            
            # Database operations
            'list_tables': [
                r'list tables?',
                r'show tables?',
                r'what tables?',
                r'database tables?',
                r'table list'
            ],
            'query_database': [
                r'query database',
                r'run sql',
                r'execute query',
                r'database query',
                r'select from',
                r'get data',
                r'find records',
                r'query:',
                r'sql:',
                r'select\s+',
                r'count\s+',
                r'sum\s+',
                r'query\s+'
            ],
            'describe_table': [
                r'describe table',
                r'table structure',
                r'table schema',
                r'columns? in',
                r'table info',
                r'show.*structure',
                r'structure.*table',
                r'schema.*table',
                r'columns.*table'
            ],
            
            # Memory operations
            'store_memory': [
                r'remember',
                r'store',
                r'save information',
                r'keep note',
                r'store data'
            ],
            'retrieve_memory': [
                r'retrieve',
                r'get information',
                r'remember',
                r'recall',
                r'get data'
            ],
            'list_memories': [
                r'list memories?',
                r'show memories?',
                r'what memories?',
                r'stored data'
            ]
        }
        
        self.parameter_extractors = {
            'path': [
                r'path[:\s]+([^\s]+)',
                r'file[:\s]+([^\s]+)',
                r'in\s+([^\s]+)',
                r'from\s+([^\s]+)',
                r'to\s+([^\s]+)'
            ],
            'content': [
                r'content[:\s]+(.+)',
                r'text[:\s]+(.+)',
                r'write[:\s]+(.+)',
                r'data[:\s]+(.+)'
            ],
            'query': [
                r'query[:\s]+(.+)',
                r'sql[:\s]+(.+)',
                r'select[:\s]+(.+)',
                r'find[:\s]+(.+)'
            ],
            'table_name': [
                r'([a-zA-Z_][a-zA-Z0-9_]*) table',
                r'table\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'structure.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'schema.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'columns.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'table[:\s]+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'in\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'of\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            ],
            'key': [
                r'key[:\s]+([^\s]+)',
                r'name[:\s]+([^\s]+)',
                r'as\s+([^\s]+)'
            ],
            'value': [
                r'value[:\s]+(.+)',
                r'data[:\s]+(.+)',
                r'information[:\s]+(.+)'
            ]
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return tool execution plan"""
        query_lower = query.lower().strip()
        
        # Find matching tool
        matched_tool = self._find_matching_tool(query_lower)
        if not matched_tool:
            return {
                'success': False,
                'error': 'No matching tool found for your query',
                'suggestions': self._get_suggestions(query_lower)
            }
        
        # Extract parameters
        parameters = self._extract_parameters(query_lower, matched_tool)
        
        # Validate parameters
        validation_result = self._validate_parameters(matched_tool, parameters)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': f'Missing required parameters: {", ".join(validation_result["missing"])}',
                'tool': matched_tool,
                'extracted_parameters': parameters,
                'suggestions': self._get_parameter_suggestions(matched_tool)
            }
        
        return {
            'success': True,
            'tool': matched_tool,
            'parameters': parameters,
            'confidence': self._calculate_confidence(query_lower, matched_tool, parameters)
        }
    
    def _find_matching_tool(self, query: str) -> Optional[str]:
        """Find the best matching tool for the query"""
        best_match = None
        best_score = 0
        
        for tool, patterns in self.tool_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    # Calculate confidence score
                    score = len(re.findall(pattern, query))
                    if score > best_score:
                        best_score = score
                        best_match = tool
        
        return best_match
    
    def _extract_parameters(self, query: str, tool: str) -> Dict[str, Any]:
        """Extract parameters from the query"""
        parameters = {}
        
        # Get required parameters for the tool
        required_params = self._get_required_parameters(tool)
        
        for param_name, patterns in self.parameter_extractors.items():
            if param_name in required_params:
                for pattern in patterns:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        parameters[param_name] = match.group(1).strip()
                        break
        
        return parameters
    
    def _get_required_parameters(self, tool: str) -> List[str]:
        """Get required parameters for a tool"""
        param_map = {
            'list_directory': ['path'],
            'read_file': ['path'],
            'write_file': ['path', 'content'],
            'list_tables': [],
            'query_database': ['query'],
            'describe_table': ['table_name'],
            'store_memory': ['key', 'value'],
            'retrieve_memory': ['key'],
            'list_memories': []
        }
        return param_map.get(tool, [])
    
    def _validate_parameters(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required parameters are present"""
        required = self._get_required_parameters(tool)
        missing = [param for param in required if param not in parameters]
        
        return {
            'valid': len(missing) == 0,
            'missing': missing
        }
    
    def _calculate_confidence(self, query: str, tool: str, parameters: Dict[str, Any]) -> float:
        """Calculate confidence score for the match"""
        base_confidence = 0.7
        
        # Increase confidence if parameters are extracted
        param_confidence = len(parameters) / len(self._get_required_parameters(tool)) if self._get_required_parameters(tool) else 1.0
        
        # Increase confidence for exact pattern matches
        pattern_confidence = 0.0
        for pattern in self.tool_patterns.get(tool, []):
            if re.search(pattern, query):
                pattern_confidence += 0.1
        
        return min(1.0, base_confidence + (param_confidence * 0.2) + pattern_confidence)
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Get suggestions for similar queries"""
        suggestions = []
        
        # Extract key words from query
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Find tools that might match
        for tool, patterns in self.tool_patterns.items():
            for pattern in patterns:
                pattern_words = re.findall(r'\b\w+\b', pattern)
                if any(word in pattern_words for word in words):
                    suggestions.append(f"Try: {self._get_tool_description(tool)}")
                    break
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _get_parameter_suggestions(self, tool: str) -> List[str]:
        """Get suggestions for missing parameters"""
        suggestions = []
        required = self._get_required_parameters(tool)
        
        for param in required:
            if param == 'path':
                suggestions.append("Specify a file path, e.g., '/path/to/file.txt'")
            elif param == 'content':
                suggestions.append("Provide the content to write")
            elif param == 'query':
                suggestions.append("Provide a SQL query, e.g., 'SELECT * FROM users'")
            elif param == 'table_name':
                suggestions.append("Specify a table name")
            elif param == 'key':
                suggestions.append("Provide a key name for storage")
            elif param == 'value':
                suggestions.append("Provide the value to store")
        
        return suggestions
    
    def _get_tool_description(self, tool: str) -> str:
        """Get human-readable description of a tool"""
        descriptions = {
            'list_directory': 'List files in a directory',
            'read_file': 'Read contents of a file',
            'write_file': 'Write content to a file',
            'list_tables': 'List database tables',
            'query_database': 'Execute SQL queries',
            'describe_table': 'Get table structure',
            'store_memory': 'Store information in memory',
            'retrieve_memory': 'Retrieve stored information',
            'list_memories': 'List all stored memories'
        }
        return descriptions.get(tool, tool)
    
    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available natural language commands"""
        commands = []
        
        for tool, patterns in self.tool_patterns.items():
            commands.append({
                'tool': tool,
                'description': self._get_tool_description(tool),
                'examples': self._get_examples(tool),
                'required_parameters': self._get_required_parameters(tool)
            })
        
        return commands
    
    def _get_examples(self, tool: str) -> List[str]:
        """Get example queries for a tool"""
        examples = {
            'list_directory': [
                'List files in /home/user',
                'Show contents of documents folder',
                'What files are in the current directory?'
            ],
            'read_file': [
                'Read the file config.txt',
                'Show content of readme.md',
                'Open the file /path/to/data.json'
            ],
            'write_file': [
                'Write "Hello World" to greeting.txt',
                'Create a file notes.txt with my notes',
                'Save data to output.csv'
            ],
            'list_tables': [
                'List all tables in the database',
                'Show database tables',
                'What tables are available?'
            ],
            'query_database': [
                'Query: SELECT * FROM users',
                'Find all records in the products table',
                'Run SQL: SELECT COUNT(*) FROM orders'
            ],
            'describe_table': [
                'Describe the users table',
                'Show structure of products table',
                'What columns are in the orders table?'
            ],
            'store_memory': [
                'Remember that John likes pizza',
                'Store the API key as "api_key"',
                'Save my preferences as "user_prefs"'
            ],
            'retrieve_memory': [
                'Get the stored API key',
                'Retrieve user preferences',
                'What did I remember about John?'
            ],
            'list_memories': [
                'List all stored memories',
                'Show what I have stored',
                'What information is saved?'
            ]
        }
        return examples.get(tool, [])
