# 🔑 **OpenAI API Key Setup Guide**

## **Where to Put Your OpenAI API Key**

### **Option 1: Edit the Run Script (Easiest)**

1. **Open the run script:**
   ```bash
   nano run_local.sh
   ```

2. **Find this line:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Replace with your actual key:**
   ```bash
   export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
   ```

4. **Save and run:**
   ```bash
   ./run_local.sh
   ```

### **Option 2: Set Environment Variable (Terminal)**

```bash
# Set for current session
export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"

# Run the application
source venv/bin/activate
streamlit run app_simple.py --server.port 8501
```

### **Option 3: Create .env File (Recommended for Development)**

1. **Create .env file:**
   ```bash
   echo "OPENAI_API_KEY=sk-your-actual-openai-api-key-here" > .env
   ```

2. **Update run script to load .env:**
   ```bash
   # Add this line to run_local.sh after "source venv/bin/activate"
   source .env 2>/dev/null || true
   ```

### **Option 4: Set in Your Shell Profile (Permanent)**

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## 🚀 **Quick Start with API Key**

### **Method 1: One-Time Setup**
```bash
# Set the key
export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"

# Run the application
./run_local.sh
```

### **Method 2: Edit Script**
```bash
# Edit the script
nano run_local.sh

# Change this line:
export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"

# Save and run
./run_local.sh
```

### **Method 3: Direct Command**
```bash
# Set key and run in one command
OPENAI_API_KEY="sk-your-actual-openai-api-key-here" ./run_local.sh
```

## 🔍 **How to Get Your OpenAI API Key**

1. **Go to OpenAI Platform:**
   - Visit: https://platform.openai.com/api-keys

2. **Sign in or Create Account:**
   - Use your OpenAI account
   - Create account if needed

3. **Create New API Key:**
   - Click "Create new secret key"
   - Give it a name (e.g., "MCP Hub")
   - Copy the key (starts with `sk-`)

4. **Add Billing Information:**
   - Add payment method to your OpenAI account
   - Set usage limits if desired

## ⚠️ **Security Notes**

### **Never Commit API Keys to Git:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
```

### **Use Environment Variables:**
- ✅ **Good**: `export OPENAI_API_KEY="sk-..."`
- ❌ **Bad**: Hardcoding in source code

### **Check Your Key Format:**
- ✅ **Correct**: `sk-proj-abc123...` (starts with `sk-`)
- ❌ **Wrong**: `sk-your-actual-openai-api-key-here`

## 🧪 **Test Your Setup**

### **Test API Key:**
```bash
# Test if key is set
echo $OPENAI_API_KEY

# Test with curl
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### **Test Application:**
```bash
# Run with your key
export OPENAI_API_KEY="sk-your-actual-key"
./run_local.sh
```

## 🎯 **Which Version to Use**

### **Demo Version (No API Key Required):**
```bash
# Works without OpenAI
streamlit run app_working.py --server.port 8501
```

### **Full Version (Requires API Key):**
```bash
# Needs OpenAI API key
export OPENAI_API_KEY="sk-your-key"
streamlit run app_simple.py --server.port 8501
```

## 🚀 **Ready to Go!**

Once you set your API key, your MCP Hub will have:
- ✅ **AI Processing**: Real OpenAI integration
- ✅ **Tool Execution**: MCP server connections
- ✅ **Smart Responses**: AI-powered tool selection
- ✅ **Full Functionality**: Complete MCP Hub experience

**Set your key and run: `./run_local.sh`** 🎉
