# 🔒 Security Guidelines for MCP Hub

## ⚠️ **IMPORTANT: API Key Security**

### **Never Commit API Keys**
- ❌ **NEVER** hardcode API keys in source code
- ❌ **NEVER** commit `.env` files with real keys
- ❌ **NEVER** include API keys in documentation examples
- ✅ **ALWAYS** use environment variables
- ✅ **ALWAYS** use placeholder values in examples

### **Safe Practices**
1. **Use Environment Variables**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export GOOGLE_API_KEY="your-key-here"
   ```

2. **Use .env Files (Not Committed)**
   ```bash
   cp env.example .env
   # Edit .env with your real keys
   # .env is in .gitignore
   ```

3. **Use Placeholder Values in Documentation**
   ```bash
   # ✅ Good
   export GOOGLE_API_KEY="your-google-api-key-here"
   
   # ❌ Bad
   export GOOGLE_API_KEY="AIzaSyDvfc7dDWbnSajHDbvYOL9DIWWyilLcgqE"
   ```

## 🛡️ **Security Checklist**

### **Before Committing:**
- [ ] No hardcoded API keys in code
- [ ] No real API keys in documentation
- [ ] .env file is in .gitignore
- [ ] All examples use placeholders
- [ ] No sensitive data in commit messages

### **Before Pushing to GitHub:**
- [ ] Run `git grep` to check for exposed keys
- [ ] Verify .gitignore is working
- [ ] Check all documentation files
- [ ] Review commit history

## 🔍 **Security Commands**

### **Check for Exposed Keys:**
```bash
# Check for Google API keys
git grep -n "AIza" HEAD

# Check for OpenAI API keys
git grep -n "sk-" HEAD

# Check for any API key patterns
git grep -n "api.*key" HEAD
```

### **Remove Sensitive Data:**
```bash
# If keys were committed, remove them
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch file-with-keys' \
  --prune-empty --tag-name-filter cat -- --all
```

## 🚨 **If API Keys Are Exposed**

### **Immediate Actions:**
1. **Revoke the exposed keys** immediately
2. **Generate new API keys**
3. **Remove keys from git history**
4. **Update all documentation**
5. **Notify team members**

### **Git History Cleanup:**
```bash
# Remove sensitive file from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch sensitive-file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push to remote (DANGEROUS - coordinate with team)
git push origin --force --all
```

## 📋 **Repository Security Status**

✅ **Current Status: SECURE**
- No hardcoded API keys in code
- All documentation uses placeholders
- .gitignore properly configured
- Environment variables properly implemented

## 🔐 **API Key Management**

### **For Development:**
```bash
# Use .env file (not committed)
echo "OPENAI_API_KEY=your-key" > .env
echo "GOOGLE_API_KEY=your-key" >> .env
```

### **For Production:**
- Use secure environment variable injection
- Use secret management services
- Never log API keys
- Rotate keys regularly

## 📞 **Security Contact**

If you discover a security vulnerability:
1. **DO NOT** create a public issue
2. **DO NOT** commit fixes with sensitive data
3. Contact the maintainer privately
4. Follow responsible disclosure practices

---

**Remember: Security is everyone's responsibility! 🔒**
