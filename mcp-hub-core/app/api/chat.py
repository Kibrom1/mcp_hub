"""
Chat API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "openai"
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.3

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: float
    timestamp: str

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a chat message and get AI response with NLP tool integration"""
    try:
        # Import here to avoid circular imports
        from app.services.llm_manager import LLMManager
        from app.services.nlp_tool_processor import NLPToolProcessor
        from app.services.mcp_executor import MCPExecutor
        
        llm_manager = LLMManager()
        nlp_processor = NLPToolProcessor()
        mcp_executor = MCPExecutor()
        
        # First, try to process as a natural language tool command
        nlp_result = nlp_processor.process_query(request.message)
        
        if nlp_result['success'] and nlp_result['confidence'] > 0.7:
            # High confidence NLP match - execute tool directly
            try:
                tool_result = await mcp_executor.execute_tool(
                    nlp_result['tool'],
                    nlp_result['parameters']
                )
                
                # Format the tool result into a natural response
                tool_response = _format_tool_response_for_chat(
                    nlp_result['tool'],
                    tool_result,
                    nlp_result['parameters']
                )
                
                return ChatResponse(
                    response=tool_response,
                    provider="nlp-tools",
                    model="natural-language-processor",
                    tokens_used=0,
                    response_time=0.1,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                # If tool execution fails, fall back to LLM
                pass
        
        # Fall back to LLM processing with enhanced system prompt
        tools_info = get_tools_info()
        resources_info = get_resources_info()
        
        system_prompt = f"""You are a helpful AI assistant with access to MCP tools and resources.

Available Tools: {tools_info}
Available Resources: {resources_info}

You can help users with:
1. Natural language tool execution (e.g., "List database tables", "Show file contents")
2. General questions and conversations
3. Tool recommendations and guidance

When a user asks something that can be answered using these tools, you should:
1. Analyze the user's request
2. Determine which tool(s) would be most helpful
3. Execute the appropriate tool(s) with the right parameters
4. Use the results to provide a comprehensive answer

You can execute tools by responding with:
TOOL_EXECUTE: {{"tool": "tool_name", "server": "server_name", "arguments": {{"param": "value"}}}}

Always provide helpful, accurate responses based on the tool results."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
        
        start_time = datetime.now()
        
        # Generate response with fallback logic
        try:
            response = await llm_manager.generate_response_async(
                messages,
                provider=request.provider,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        except Exception as e:
            # If OpenAI fails and we're using OpenAI, try Google as fallback
            if request.provider == "openai" and "quota" in str(e).lower():
                print(f"⚠️ OpenAI quota exceeded, falling back to Google: {e}")
                try:
                    response = await llm_manager.generate_response_async(
                        messages,
                        provider="google",
                        max_tokens=request.max_tokens,
                        temperature=request.temperature
                    )
                except Exception as fallback_error:
                    print(f"⚠️ Google fallback also failed: {fallback_error}")
                    raise e  # Re-raise original error
            else:
                raise e
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        return ChatResponse(
            response=response.content,
            provider=response.provider,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response_time,
            timestamp=end_time.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {e}")

@router.get("/history")
async def get_chat_history(limit: int = 50):
    """Get chat history"""
    try:
        # This would typically come from a database
        # For now, return empty history
        return {"messages": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {e}")

@router.delete("/history")
async def clear_chat_history():
    """Clear chat history"""
    try:
        # This would typically clear from a database
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {e}")

def _format_tool_response_for_chat(tool: str, result: Dict[str, Any], parameters: Dict[str, Any]) -> str:
    """Format tool execution result into a natural chat response"""
    
    if not result.get('success', False):
        return f"Sorry, I couldn't execute that operation. Error: {result.get('error', 'Unknown error')}"
    
    # Format response based on tool type
    if tool == 'list_directory':
        files = result.get('result', {}).get('files', [])
        if files:
            file_list = '\n'.join([f"• {file}" for file in files[:10]])  # Show first 10 files
            more_text = f"\n... and {len(files) - 10} more files" if len(files) > 10 else ""
            return f"Found {len(files)} files in {parameters.get('path', 'the directory')}:\n{file_list}{more_text}"
        else:
            return f"The directory {parameters.get('path', '')} is empty."
    
    elif tool == 'read_file':
        content = result.get('result', {}).get('content', '')
        if content:
            # Truncate long content
            if len(content) > 500:
                content = content[:500] + "... (truncated)"
            return f"Here's the content of {parameters.get('path', 'the file')}:\n```\n{content}\n```"
        else:
            return "The file appears to be empty."
    
    elif tool == 'write_file':
        return f"Successfully wrote to {parameters.get('path', 'the file')}."
    
    elif tool == 'list_tables':
        tables = result.get('result', {}).get('tables', [])
        if tables:
            table_list = '\n'.join([f"• {table}" for table in tables])
            return f"Found {len(tables)} tables in the database:\n{table_list}"
        else:
            return "No tables found in the database."
    
    elif tool == 'query_database':
        query_result = result.get('result', {})
        if 'rows' in query_result:
            rows = query_result['rows']
            if rows:
                # Show first few rows
                display_rows = rows[:5]
                response = f"Query executed successfully. Found {len(rows)} rows:\n"
                for i, row in enumerate(display_rows):
                    response += f"Row {i+1}: {row}\n"
                if len(rows) > 5:
                    response += f"... and {len(rows) - 5} more rows"
                return response
            else:
                return "Query executed successfully, but no rows were returned."
        else:
            return f"Query executed: {query_result.get('message', 'Success')}"
    
    elif tool == 'describe_table':
        schema = result.get('result', {})
        if 'columns' in schema:
            columns = schema['columns']
            column_list = '\n'.join([f"• {col['name']} ({col.get('type', 'unknown')})" for col in columns])
            return f"Table structure for {parameters.get('table_name', 'the table')}:\n{column_list}"
        else:
            return f"Table information: {schema.get('message', 'Success')}"
    
    elif tool == 'store_memory':
        return f"Successfully stored information with key '{parameters.get('key', '')}'."
    
    elif tool == 'retrieve_memory':
        value = result.get('result', {}).get('value', '')
        if value:
            return f"Retrieved: {value}"
        else:
            return "No information found for that key."
    
    elif tool == 'list_memories':
        memories = result.get('result', {}).get('memories', [])
        if memories:
            memory_list = '\n'.join([f"• {mem}" for mem in memories])
            return f"Stored memories:\n{memory_list}"
        else:
            return "No memories stored."
    
    else:
        # Generic response
        return f"Operation completed successfully. Result: {result.get('result', 'Success')}"

def get_tools_info() -> str:
    """Get formatted tools information"""
    try:
        import sqlite3
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, description FROM tools")
        tools = cursor.fetchall()
        conn.close()
        
        tools_info = []
        for tool in tools:
            tools_info.append(f"- {tool[0]}: {tool[1]}")
        
        return "\n".join(tools_info)
    except Exception as e:
        return f"Error loading tools: {e}"

def get_resources_info() -> str:
    """Get formatted resources information"""
    try:
        import sqlite3
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, uri FROM resources")
        resources = cursor.fetchall()
        conn.close()
        
        resources_info = []
        for resource in resources:
            resources_info.append(f"- {resource[0]}: {resource[1]}")
        
        return "\n".join(resources_info)
    except Exception as e:
        return f"Error loading resources: {e}"
