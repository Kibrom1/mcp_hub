# 🔑 Google API Key Setup for MCP Hub

## 📋 **How to Get Google API Key**

### **Step 1: Get API Key**
1. **Visit**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the API key** (starts with `AIza...`)

### **Step 2: Configure in MCP Hub**

#### **Method 1: Environment Variable (Recommended)**
```bash
# Set the Google API key
export GOOGLE_API_KEY="your-google-api-key-here"

# Run the multi-LLM app
./run_multi_llm.sh
```

#### **Method 2: Edit Run Script**
Edit `run_multi_llm.sh` and uncomment this line:
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

#### **Method 3: Create .env File**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your-google-api-key-here" > .env

# Source the environment
source .env

# Run the app
./run_multi_llm.sh
```

## 🚀 **Quick Setup Commands**

### **1. Set Google API Key**
```bash
# Replace with your actual API key
export GOOGLE_API_KEY="AIza-your-actual-key-here"
```

### **2. Test Configuration**
```bash
# Check if Google is configured
python setup_llm_providers.py --check
```

### **3. Run Multi-LLM App**
```bash
# Start the app with Google support
./run_multi_llm.sh
```

## 🎯 **What You'll See**

Once configured, you'll see:
- **✅ Google configured** in the startup messages
- **Google** option in the provider dropdown
- **Gemini model** available for selection

## 🔧 **Troubleshooting**

### **If Google doesn't appear:**
1. **Check API key**: Make sure it starts with `AIza`
2. **Check environment**: Run `echo $GOOGLE_API_KEY`
3. **Restart app**: Stop and restart the application

### **If you get errors:**
1. **Verify API key**: Test at https://makersuite.google.com/
2. **Check permissions**: Ensure API access is enabled
3. **Check quota**: Verify you have API usage remaining

## 📊 **Google Gemini Models Available**

- **gemini-pro**: General purpose model
- **gemini-pro-vision**: Image understanding model

## 🎉 **Ready to Use!**

Once you set your Google API key, you can:
- **Select Google** from the provider dropdown
- **Use Gemini models** for AI responses
- **Compare responses** between different providers

**Your MCP Hub will automatically detect and enable Google Gemini! 🚀**
