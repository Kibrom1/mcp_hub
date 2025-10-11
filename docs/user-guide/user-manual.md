# 👤 User Manual

Complete guide to using MCP Hub effectively.

## 🎯 **Overview**

MCP Hub is a tool integration platform that connects AI assistants with your local tools and resources through the Model Context Protocol (MCP).

## 🖥️ **Interface Overview**

### **Main Chat Interface**
- **Chat Input**: Type your questions and requests
- **Message History**: View conversation history
- **AI Responses**: Get intelligent responses with tool execution

### **Sidebar Configuration**
- **LLM Provider**: Switch between OpenAI and Google Gemini
- **Debug Mode**: Enable detailed execution information
- **Tools & Resources**: View available MCP tools

## 🛠️ **Working with Tools**

### **Available Tools**

#### **Filesystem Server**
- **read_file**: Read contents of any file
- **write_file**: Create or modify files
- **list_directory**: Browse directory contents

#### **Memory Server**
- **store_memory**: Save information for later
- **retrieve_memory**: Get stored information
- **list_memories**: See all stored memories

### **Using Tools in Chat**

The AI can automatically use tools when you ask questions like:

```
"List files in my Documents folder"
"Read my project README file"
"Create a Python script for data analysis"
"Store notes about this meeting"
```

## 📁 **File Operations**

### **Creating Files**

#### **Using Templates**
1. Go to **Sidebar** → **Resources** → **filesystem**
2. Click template buttons:
   - **📝 Text File**: Simple text file
   - **🐍 Python Script**: Python code with shebang
   - **📄 Markdown**: Markdown document

#### **Manual Creation**
1. Enter **File Path**: `/path/to/your/file.txt`
2. Add **Content**: Write your file content
3. Click **"📝 Create File"**

### **Reading Files**
1. Enter **File Path**: `/path/to/existing/file.txt`
2. Click **"📖 Read File"**
3. View file contents in the interface

### **Browsing Directories**
1. Enter **Directory Path**: `/Users/YourName/Documents`
2. Click **"📂 Browse Directory"**
3. See directory contents

## 💾 **Memory Management**

### **Storing Information**
Ask the AI to store information:
```
"Store a memory about our project goals"
"Remember that the meeting is at 3 PM"
"Save notes about the API documentation"
```

### **Retrieving Information**
Ask the AI to retrieve stored information:
```
"What memories do I have stored?"
"Retrieve the memory about project goals"
"Show me all my saved notes"
```

## 🤖 **LLM Providers**

### **OpenAI (GPT-4o-mini)**
- **Best for**: Code generation, complex reasoning
- **Features**: Tool execution, detailed responses
- **Setup**: Requires OpenAI API key

### **Google Gemini (gemini-2.0-flash)**
- **Best for**: Fast responses, general tasks
- **Features**: Quick tool execution, efficient processing
- **Setup**: Requires Google API key

### **Switching Providers**
1. Go to **Sidebar** → **LLM Provider**
2. Select your preferred provider
3. Start chatting - the AI will use the selected provider

## 🐛 **Debug Mode**

Enable debug mode to see:
- **Tool Execution Details**: Which tools are being used
- **Response Times**: How long operations take
- **Error Information**: Detailed error messages
- **Processing Info**: Internal system information

### **Enabling Debug Mode**
1. Go to **Sidebar** → **Debug Mode**
2. Check the box to enable
3. See detailed information in responses

## 🎯 **Best Practices**

### **Effective Queries**
- **Be Specific**: "List Python files in my project" vs "List files"
- **Use Context**: "Create a README for my Python project"
- **Ask for Help**: "What tools can help me with file management?"

### **File Management**
- **Use Templates**: Start with provided templates
- **Organize Paths**: Use clear, organized file paths
- **Backup Important Files**: Don't rely solely on MCP Hub

### **Memory Usage**
- **Store Key Information**: Important notes and reminders
- **Use Descriptive Keys**: "project-goals" vs "notes"
- **Regular Cleanup**: Remove outdated memories

## 🆘 **Troubleshooting**

### **Common Issues**

#### **"No tools available"**
```bash
# Re-discover tools
python discover_tools.py
```

#### **"API key not found"**
```bash
# Set your API keys
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

#### **"Tool execution failed"**
- Check file paths are correct
- Ensure you have permissions
- Try with simpler requests first

#### **"Application won't start"**
```bash
# Kill existing processes
pkill -f streamlit
./run.sh
```

### **Getting Help**
- **Debug Mode**: Enable for detailed error information
- **Tool Status**: Check sidebar for available tools
- **Logs**: Check console output for error messages

## 🚀 **Advanced Usage**

### **Custom Tool Integration**
- Add your own MCP servers
- Configure custom tools
- Integrate with external services

### **Batch Operations**
- Process multiple files
- Bulk memory operations
- Automated workflows

### **Integration Examples**
- Connect to databases
- Integrate with cloud services
- Custom automation scripts

---

**Happy using MCP Hub! 🎉**
