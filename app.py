#!/usr/bin/env python3
"""
MCP Hub - Simplified Tool-Aware Multi-LLM Application
This version avoids complex package imports and works standalone
"""

import streamlit as st
import asyncio
import time
import json
import sqlite3
import subprocess
from datetime import datetime
from llm_providers import get_llm_manager

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="MCP Hub - Tool-Aware Multi-LLM",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    render_app()

def render_app():
    """Render the main application"""
    
    # Header
    st.title("🤖 MCP Hub - Tool-Aware Multi-LLM")
    st.caption("AI Assistant with access to your local MCP tools and resources")
    
    # Initialize LLM manager
    try:
        llm_manager = get_llm_manager()
        available_providers = llm_manager.list_available_providers()
        
        if not available_providers:
            st.error("❌ No LLM providers available. Please check your API keys.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Failed to initialize LLM manager: {e}")
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Provider selection
        selected_provider = st.selectbox(
            "🤖 LLM Provider",
            available_providers,
            index=0,
            help="Select which LLM provider to use for responses"
        )
        
        # Debug mode toggle
        if st.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode):
            st.session_state.debug_mode = True
        else:
            st.session_state.debug_mode = False
        
        # Load and display servers, tools, and resources
        try:
            conn = sqlite3.connect('mcp.db')
            cursor = conn.cursor()
            
            # Get servers
            cursor.execute("SELECT name, uri, enabled FROM servers")
            servers = cursor.fetchall()
            
            # Get tools
            cursor.execute("SELECT server_name, name, description, parameters FROM tools")
            tools = cursor.fetchall()
            
            # Get resources
            cursor.execute("SELECT server_name, name, uri FROM resources")
            resources = cursor.fetchall()
            
            conn.close()
            
            st.header("🛠️ Available Tools & Resources")
            
            if not servers:
                st.warning("⚠️ No servers configured")
            else:
                for server_name, server_uri, enabled in servers:
                    status = "✅ Enabled" if enabled else "❌ Disabled"
                    st.subheader(f"🖥️ {server_name} {status}")
                    
                    # Tools for this server
                    server_tools = [t for t in tools if t[0] == server_name]
                    if server_tools:
                        with st.expander(f"🔧 Tools ({len(server_tools)})"):
                            for tool in server_tools:
                                st.write(f"**{tool[1]}**")
                                st.caption(tool[2])
                                # Show parameters in a cleaner format without JSON
                                if tool[3]:  # parameters
                                    try:
                                        params = json.loads(tool[3])
                                        if params:
                                            param_list = []
                                            for key, value in params.items():
                                                if isinstance(value, dict) and 'type' in value:
                                                    param_list.append(f"{key} ({value.get('type', 'string')})")
                                                else:
                                                    param_list.append(key)
                                            st.caption(f"📝 Parameters: {', '.join(param_list)}")
                                    except:
                                        st.caption(f"📝 Parameters: {tool[3]}")
                    else:
                        st.caption("No tools available")
                    
                    # Resources for this server
                    server_resources = [r for r in resources if r[0] == server_name]
                    if server_resources:
                        with st.expander(f"📁 Resources ({len(server_resources)})"):
                            for resource in server_resources:
                                st.write(f"**{resource[1]}**")
                                # Display resource URI in a cleaner format
                                if resource[2].startswith("sqlite://"):
                                    st.caption(f"🗄️ Database: {resource[2].replace('sqlite://', '')}")
                                elif resource[2].startswith("memory://"):
                                    st.caption("💾 Memory Store")
                                elif resource[2].startswith("/"):
                                    st.caption(f"📂 Directory: {resource[2]}")
                                else:
                                    st.caption(f"🔗 URI: {resource[2]}")
                                
                                # Add database interface for SQLite resources
                                if server_name == "sqlite" and resource[1] == "mcp_database":
                                    st.write("---")
                                    st.subheader("🗄️ Database Operations")
                                    
                                    # Database query interface
                                    st.write("**Query Database**")
                                    
                                    # Query input
                                    db_query = st.text_area(
                                        "📝 SQL Query", 
                                        placeholder="SELECT * FROM servers WHERE enabled = 1",
                                        height=100,
                                        help="Enter a SQL query to execute on the database",
                                        key=f"db_query_{server_name}"
                                    )
                                    
                                    # Quick query buttons
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        if st.button("📊 List Tables", key=f"list_tables_{server_name}"):
                                            try:
                                                result = execute_mcp_tool("sqlite", "list_tables", {})
                                                st.success("📊 Database tables retrieved")
                                                if isinstance(result, dict) and 'result' in result:
                                                    tables = result['result']
                                                    if isinstance(tables, list):
                                                        st.write("**Available Tables:**")
                                                        for table in tables:
                                                            st.write(f"• {table}")
                                                    else:
                                                        st.write(f"Tables: {tables}")
                                                else:
                                                    st.write(f"Result: {result}")
                                            except Exception as e:
                                                st.error(f"❌ Failed to list tables: {e}")
                                    
                                    with col2:
                                        if st.button("🔍 Describe Table", key=f"describe_table_{server_name}"):
                                            table_name = st.text_input("Table Name", placeholder="servers", key=f"table_name_{server_name}")
                                            if table_name:
                                                try:
                                                    result = execute_mcp_tool("sqlite", "describe_table", {"table_name": table_name})
                                                    st.success(f"📋 Schema for table '{table_name}'")
                                                    if isinstance(result, dict) and 'result' in result:
                                                        schema = result['result']
                                                        if isinstance(schema, dict) and 'columns' in schema:
                                                            st.write("**Table Schema:**")
                                                            for col in schema['columns']:
                                                                st.write(f"• **{col.get('name', 'Unknown')}** ({col.get('type', 'Unknown')})")
                                                        else:
                                                            st.write(f"Schema: {schema}")
                                                    else:
                                                        st.write(f"Result: {result}")
                                                except Exception as e:
                                                    st.error(f"❌ Failed to describe table: {e}")
                                    
                                    with col3:
                                        if st.button("📄 Sample Data", key=f"sample_data_{server_name}"):
                                            table_name = st.text_input("Table Name", placeholder="servers", key=f"sample_table_{server_name}")
                                            if table_name:
                                                try:
                                                    result = execute_mcp_tool("sqlite", "get_table_data", {"table_name": table_name, "limit": 5})
                                                    st.success(f"📄 Sample data from '{table_name}'")
                                                    if isinstance(result, dict) and 'result' in result:
                                                        data = result['result']
                                                        if isinstance(data, dict) and 'columns' in data and 'rows' in data:
                                                            st.write("**Sample Data:**")
                                                            # Show as a simple table format
                                                            for i, row in enumerate(data['rows'][:5]):  # Limit to 5 rows
                                                                st.write(f"Row {i+1}: {row}")
                                                        else:
                                                            st.write(f"Data: {data}")
                                                    else:
                                                        st.write(f"Result: {result}")
                                                except Exception as e:
                                                    st.error(f"❌ Failed to get sample data: {e}")
                                    
                                    with col4:
                                        if st.button("▶️ Execute Query", type="primary", key=f"execute_query_{server_name}"):
                                            if db_query:
                                                try:
                                                    result = execute_mcp_tool("sqlite", "query_database", {"query": db_query})
                                                    st.success("✅ Query executed successfully")
                                                    if isinstance(result, dict) and 'result' in result:
                                                        query_result = result['result']
                                                        if isinstance(query_result, dict) and 'columns' in query_result and 'rows' in query_result:
                                                            st.write("**Query Results:**")
                                                            # Show columns
                                                            st.write(f"Columns: {', '.join(query_result['columns'])}")
                                                            # Show rows
                                                            for i, row in enumerate(query_result['rows'][:10]):  # Limit to 10 rows
                                                                st.write(f"Row {i+1}: {row}")
                                                        else:
                                                            st.write(f"Result: {query_result}")
                                                    else:
                                                        st.write(f"Result: {result}")
                                                except Exception as e:
                                                    st.error(f"❌ Query failed: {e}")
                                            else:
                                                st.warning("⚠️ Please enter a SQL query")
                                
                                # Add file creation interface for filesystem resources
                                elif server_name == "filesystem" and resource[1] == "file_system":
                                    st.write("---")
                                    st.subheader("📝 File Operations")
                                    
                                    # File creation interface
                                    st.write("**Create New File**")
                                    
                                    # File path input
                                    file_path = st.text_input(
                                        "📁 File Path", 
                                        placeholder="/Users/YourName/Documents/new_file.txt",
                                        help="Enter the full path where you want to create the file",
                                        key=f"file_path_{server_name}"
                                    )
                                    
                                    # File content input
                                    file_content = st.text_area(
                                        "📄 File Content",
                                        placeholder="Enter the content for your new file...",
                                        height=150,
                                        help="Write the content that should go in the file",
                                        key=f"file_content_{server_name}"
                                    )
                                    
                                    # Action buttons
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button("📝 Create File", type="primary", key=f"create_{server_name}"):
                                            if file_path and file_content:
                                                try:
                                                    # Execute the write_file tool directly
                                                    result = execute_mcp_tool("filesystem", "write_file", {
                                                        "path": file_path, 
                                                        "content": file_content
                                                    })
                                                    st.success(f"✅ File created successfully: {file_path}")
                                                    st.json(result)
                                                except Exception as e:
                                                    st.error(f"❌ Failed to create file: {e}")
                                            else:
                                                st.warning("⚠️ Please enter both file path and content")
                                    
                                    with col2:
                                        if st.button("📂 Browse Directory", key=f"browse_{server_name}"):
                                            try:
                                                # Get directory path from file path or use default
                                                dir_path = "/Users" if not file_path else "/".join(file_path.split("/")[:-1])
                                                result = execute_mcp_tool("filesystem", "list_directory", {"path": dir_path})
                                                st.success(f"📂 Directory contents for: {dir_path}")
                                                st.json(result)
                                            except Exception as e:
                                                st.error(f"❌ Failed to list directory: {e}")
                                    
                                    with col3:
                                        if st.button("📖 Read File", key=f"read_{server_name}"):
                                            if file_path:
                                                try:
                                                    result = execute_mcp_tool("filesystem", "read_file", {"path": file_path})
                                                    st.success(f"📖 File contents of: {file_path}")
                                                    st.text_area("File Content", result.get("result", "No content"), height=200, disabled=True)
                                                except Exception as e:
                                                    st.error(f"❌ Failed to read file: {e}")
                                            else:
                                                st.warning("⚠️ Please enter a file path to read")
                                    
                                    # Quick file templates
                                    st.write("**📋 Quick Templates**")
                                    template_col1, template_col2, template_col3 = st.columns(3)
                                    
                                    with template_col1:
                                        if st.button("📝 Text File", key=f"template_text_{server_name}"):
                                            st.session_state[f"file_path_{server_name}"] = "/tmp/note.txt"
                                            st.session_state[f"file_content_{server_name}"] = "Hello World!\nThis is a simple text file."
                                            st.rerun()
                                    
                                    with template_col2:
                                        if st.button("🐍 Python Script", key=f"template_python_{server_name}"):
                                            st.session_state[f"file_path_{server_name}"] = "/tmp/script.py"
                                            st.session_state[f"file_content_{server_name}"] = """#!/usr/bin/env python3
# Simple Python script
print("Hello from MCP Hub!")
"""
                                            st.rerun()
                                    
                                    with template_col3:
                                        if st.button("📄 Markdown", key=f"template_md_{server_name}"):
                                            st.session_state[f"file_path_{server_name}"] = "/tmp/README.md"
                                            st.session_state[f"file_content_{server_name}"] = """# My Document

This is a markdown file created with MCP Hub.

## Features
- File creation
- Tool integration
- Multi-LLM support
"""
                                            st.rerun()
                    else:
                        st.caption("No resources available")
                        
        except Exception as e:
            st.error(f"❌ Failed to load tools: {e}")
    
    # Main chat interface
    st.header("💬 Chat with AI + Tools")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask me anything! I can use your local tools and resources..."):
        # Add user message
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate AI response with tool access
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking and using tools..."):
                start_time = time.time()
                
                try:
                    # Get available tools and resources for the system prompt
                    tools_info = get_tools_info()
                    resources_info = get_resources_info()
                    
                    # Create enhanced system prompt with tool access
                    system_prompt = f"""You are a helpful AI assistant with access to MCP (Model Context Protocol) tools and resources.

Available Tools:
{tools_info}

Available Resources:
{resources_info}

When a user asks something that can be answered or accomplished using these tools, you should:
1. Analyze the user's request
2. Determine which tool(s) would be most helpful
3. Execute the appropriate tool(s) with the right parameters
4. Use the results to provide a comprehensive answer

You can execute tools by responding with a special format:
TOOL_EXECUTE: {{"tool": "tool_name", "server": "server_name", "arguments": {{"param": "value"}}}}

If you need to execute multiple tools, you can chain them:
TOOL_EXECUTE: {{"tool": "tool1", "server": "server1", "arguments": {{}}}}
TOOL_EXECUTE: {{"tool": "tool2", "server": "server2", "arguments": {{}}}}

Always provide helpful, accurate responses based on the tool results."""
                    
                    # Create messages for the LLM
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                    
                    # Generate response using selected provider
                    response = asyncio.run(llm_manager.generate_response(
                        messages, 
                        provider=selected_provider,
                        max_tokens=2000,
                        temperature=0.3
                    ))
                    
                    # Check if response contains tool execution requests
                    response_content = response.content
                    tool_results = []
                    
                    if "TOOL_EXECUTE:" in response_content:
                        # Extract and execute tools
                        tool_results = execute_tools_from_response(response_content)
                        
                        # Generate final response with tool results
                        final_messages = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                            {"role": "assistant", "content": response_content},
                            {"role": "user", "content": f"Tool execution results: {json.dumps(tool_results, indent=2)}"}
                        ]
                        
                        final_response = asyncio.run(llm_manager.generate_response(
                            final_messages,
                            provider=selected_provider,
                            max_tokens=2000,
                            temperature=0.3
                        ))
                        response_content = final_response.content
                    
                    duration = time.time() - start_time
                    
                    # Format response
                    output = f"""
**AI Response:**
{response_content}
"""
                    
                    # Add tool results if any
                    if tool_results:
                        output += f"""
**Tool Execution Results:**
```json
{json.dumps(tool_results, indent=2)}
```
"""
                    
                    output += f"""
**Processing Info:**
- **Provider**: {response.provider.upper()}
- **Model**: {response.model}
- **Duration**: {response.response_time:.2f}s
"""
                    
                    if response.tokens_used:
                        output += f"- **Tokens**: {response.tokens_used}\n"
                    
                    if response.finish_reason:
                        output += f"- **Finish Reason**: {response.finish_reason}\n"
                    
                    # Add debug info if enabled
                    if st.session_state.debug_mode:
                        output += f"""
---
**Debug Info:**
- Query: {user_input}
- Provider: {response.provider}
- Model: {response.model}
- Tools Available: {len(tools)}
- Resources Available: {len(resources)}
- Success: True
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Response Time: {response.response_time:.2f}s
"""
                    
                    st.write(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                    
                except Exception as e:
                    error_msg = f"❌ Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    if st.session_state.debug_mode:
                        st.exception(e)

def get_tools_info():
    """Get formatted tools information for system prompt"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT server_name, name, description, parameters FROM tools")
        tools = cursor.fetchall()
        conn.close()
        
        tools_info = []
        for tool in tools:
            tools_info.append(f"- {tool[0]}.{tool[1]}: {tool[2]}")
            if tool[3]:  # parameters
                try:
                    params = json.loads(tool[3])
                    tools_info.append(f"  Parameters: {list(params.keys())}")
                except:
                    pass
        
        return "\n".join(tools_info) if tools_info else "No tools available"
        
    except Exception as e:
        return f"Error loading tools: {e}"

def get_resources_info():
    """Get formatted resources information for system prompt"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT server_name, name, uri FROM resources")
        resources = cursor.fetchall()
        conn.close()
        
        resources_info = []
        for resource in resources:
            resources_info.append(f"- {resource[0]}.{resource[1]}: {resource[2]}")
        
        return "\n".join(resources_info) if resources_info else "No resources available"
        
    except Exception as e:
        return f"Error loading resources: {e}"

def execute_mcp_tool(server_name, tool_name, arguments):
    """Execute an MCP tool directly"""
    try:
        if server_name == "sqlite":
            return execute_sqlite_tool(tool_name, arguments)
        elif server_name == "filesystem":
            return execute_filesystem_tool(tool_name, arguments)
        elif server_name == "memory":
            return execute_memory_tool(tool_name, arguments)
        else:
            # For other servers, return a mock response
            return {
                "server": server_name,
                "tool": tool_name,
                "arguments": arguments,
                "result": f"Mock execution of {server_name}.{tool_name}",
                "success": True
            }
    except Exception as e:
        return {
            "error": f"Tool execution failed: {e}",
            "server": server_name,
            "tool": tool_name
        }

def execute_sqlite_tool(tool_name, arguments):
    """Execute SQLite database tools"""
    import sqlite3
    import json
    
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        if tool_name == "query_database":
            query = arguments.get("query", "")
            cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": {
                        "columns": columns,
                        "rows": results,
                        "row_count": len(results)
                    },
                    "success": True
                }
            else:
                conn.commit()
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": f"Query executed successfully. Rows affected: {cursor.rowcount}",
                    "success": True
                }
        
        elif tool_name == "list_tables":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            return {
                "server": "sqlite",
                "tool": tool_name,
                "result": table_names,
                "success": True
            }
        
        elif tool_name == "describe_table":
            table_name = arguments.get("table_name", "")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema = {
                "table": table_name,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            }
            return {
                "server": "sqlite",
                "tool": tool_name,
                "result": schema,
                "success": True
            }
        
        elif tool_name == "get_table_data":
            table_name = arguments.get("table_name", "")
            limit = arguments.get("limit", 10)
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            data = {
                "table": table_name,
                "columns": columns,
                "rows": results,
                "row_count": len(results)
            }
            return {
                "server": "sqlite",
                "tool": tool_name,
                "result": data,
                "success": True
            }
        
        else:
            return {
                "server": "sqlite",
                "tool": tool_name,
                "result": f"Unknown tool: {tool_name}",
                "success": False
            }
            
    except Exception as e:
        return {
            "server": "sqlite",
            "tool": tool_name,
            "error": f"SQLite tool execution failed: {e}",
            "success": False
        }
    finally:
        conn.close()

def execute_filesystem_tool(tool_name, arguments):
    """Execute filesystem tools"""
    import os
    
    try:
        if tool_name == "read_file":
            path = arguments.get("path", "")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "server": "filesystem",
                "tool": tool_name,
                "result": content,
                "success": True
            }
        elif tool_name == "write_file":
            path = arguments.get("path", "")
            content = arguments.get("content", "")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "server": "filesystem",
                "tool": tool_name,
                "result": f"File written successfully: {path}",
                "success": True
            }
        elif tool_name == "list_directory":
            path = arguments.get("path", "")
            items = os.listdir(path)
            return {
                "server": "filesystem",
                "tool": tool_name,
                "result": items,
                "success": True
            }
        else:
            return {
                "server": "filesystem",
                "tool": tool_name,
                "result": f"Unknown tool: {tool_name}",
                "success": False
            }
    except Exception as e:
        return {
            "server": "filesystem",
            "tool": tool_name,
            "error": f"Filesystem tool execution failed: {e}",
            "success": False
        }

def execute_memory_tool(tool_name, arguments):
    """Execute memory tools"""
    import sqlite3
    import json
    
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        if tool_name == "store_memory":
            key = arguments.get("key", "")
            value = arguments.get("value", "")
            cursor.execute("""
                INSERT OR REPLACE INTO memories (key, value, created_at)
                VALUES (?, ?, datetime('now'))
            """, (key, value))
            conn.commit()
            return {
                "server": "memory",
                "tool": tool_name,
                "result": f"Memory stored: {key}",
                "success": True
            }
        elif tool_name == "retrieve_memory":
            key = arguments.get("key", "")
            cursor.execute("SELECT value FROM memories WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                return {
                    "server": "memory",
                    "tool": tool_name,
                    "result": result[0],
                    "success": True
                }
            else:
                return {
                    "server": "memory",
                    "tool": tool_name,
                    "result": f"No memory found for key: {key}",
                    "success": False
                }
        elif tool_name == "list_memories":
            cursor.execute("SELECT key, value, created_at FROM memories ORDER BY created_at DESC")
            memories = cursor.fetchall()
            return {
                "server": "memory",
                "tool": tool_name,
                "result": [{"key": m[0], "value": m[1], "created_at": m[2]} for m in memories],
                "success": True
            }
        else:
            return {
                "server": "memory",
                "tool": tool_name,
                "result": f"Unknown tool: {tool_name}",
                "success": False
            }
    except Exception as e:
        return {
            "server": "memory",
            "tool": tool_name,
            "error": f"Memory tool execution failed: {e}",
            "success": False
        }
    finally:
        conn.close()

def execute_tools_from_response(response_content):
    """Execute tools mentioned in the AI response"""
    tool_results = []
    
    try:
        # Find all TOOL_EXECUTE: lines
        lines = response_content.split('\n')
        for line in lines:
            if line.strip().startswith('TOOL_EXECUTE:'):
                # Extract JSON from the line
                json_str = line.strip().replace('TOOL_EXECUTE:', '').strip()
                try:
                    tool_request = json.loads(json_str)
                    
                    # Execute the tool
                    server_name = tool_request.get('server')
                    tool_name = tool_request.get('tool')
                    arguments = tool_request.get('arguments', {})
                    
                    if server_name and tool_name:
                        result = execute_mcp_tool(server_name, tool_name, arguments)
                        tool_results.append(result)
                    else:
                        tool_results.append({
                            'error': 'Missing server or tool name',
                            'request': tool_request
                        })
                        
                except json.JSONDecodeError as e:
                    tool_results.append({
                        'error': f'Invalid JSON in tool request: {e}',
                        'line': line
                    })
                except Exception as e:
                    tool_results.append({
                        'error': f'Tool execution failed: {e}',
                        'request': tool_request
                    })
                    
    except Exception as e:
        tool_results.append({
            'error': f'Failed to parse tool requests: {e}'
        })
    
    return tool_results

if __name__ == "__main__":
    main()
