#!/usr/bin/env python3
"""
MCP Hub - Demo Mode Application
This version works without LLM providers for demonstration purposes
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime

def main():
    """Main application entry point for demo mode"""
    st.set_page_config(
        page_title="MCP Hub - Demo Mode",
        page_icon="🔧",
        layout="wide"
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    render_demo_app()

def render_demo_app():
    """Render the demo application"""
    
    # Header
    st.title("🔧 MCP Hub - Demo Mode")
    st.caption("Tool Explorer with MCP integration (No AI providers required)")
    
    # Demo mode info
    st.info("""
    **🔧 Demo Mode Features:**
    - Explore available MCP tools and resources
    - Use interactive tool interfaces
    - Test database queries and file operations
    - No AI chat available (requires API keys)
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.warning("🔧 Demo Mode - No AI providers available")
        st.info("**Available in Demo Mode:**\n- View tools and resources\n- Use interactive tool interfaces\n- Explore database and files")
        
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
                                                result = execute_sqlite_tool("list_tables", {})
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
                                                    result = execute_sqlite_tool("describe_table", {"table_name": table_name})
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
                                                    result = execute_sqlite_tool("get_table_data", {"table_name": table_name, "limit": 5})
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
                                                    result = execute_sqlite_tool("query_database", {"query": db_query})
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
                                                    result = execute_filesystem_tool("write_file", {
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
                                                result = execute_filesystem_tool("list_directory", {"path": dir_path})
                                                st.success(f"📂 Directory contents for: {dir_path}")
                                                st.json(result)
                                            except Exception as e:
                                                st.error(f"❌ Failed to list directory: {e}")
                                    
                                    with col3:
                                        if st.button("📖 Read File", key=f"read_{server_name}"):
                                            if file_path:
                                                try:
                                                    result = execute_filesystem_tool("read_file", {"path": file_path})
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
    
    # Demo mode instructions
    st.markdown("### 🛠️ Available Demo Features:")
    st.markdown("""
    - **🗄️ Database Tools**: Query, explore, and analyze your database
    - **📁 File Operations**: Create, read, and manage files
    - **💾 Memory Tools**: Store and retrieve information
    - **🔍 Tool Discovery**: View all available MCP tools
    """)
    
    # Disable chat input in demo mode
    st.chat_input("Chat disabled in demo mode - use tool interfaces above", disabled=True)

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

if __name__ == "__main__":
    main()
