# 🔐 Encrypted API Keys Guide for MCP Hub

## 🛡️ **Security Overview**

This guide provides multiple methods to securely store and manage API keys for your MCP Hub deployment, ensuring your credentials are never exposed in plain text.

## 🔧 **Method 1: Local File Encryption (Recommended for Development)**

### **Setup:**
```bash
# Install cryptography library
pip install cryptography

# Setup encrypted keys
python secure_key_manager.py setup
```

### **Usage:**
```bash
# Load encrypted keys before running
python secure_key_manager.py load
./run.sh
```

### **Features:**
- ✅ **PBKDF2 encryption** with 100,000 iterations
- ✅ **Fernet or AES-256** encryption methods
- ✅ **Master password protection**
- ✅ **Automatic environment variable setting**

---

## 🐳 **Method 2: Docker Secrets (Recommended for Production)**

### **Setup:**
```bash
# Set master password
export MCP_MASTER_KEY="your-super-secure-master-password"

# Create Docker secrets
python docker_secure_setup.py setup
```

### **Docker Compose Configuration:**
```yaml
version: '3.8'
services:
  mcp-hub:
    image: mcp-hub:latest
    secrets:
      - api-keys
    environment:
      - MCP_MASTER_KEY=${MCP_MASTER_KEY}
    ports:
      - "8501:8501"

secrets:
  api-keys:
    external: true
    name: mcp-api-keys
```

### **Features:**
- ✅ **Docker native secrets management**
- ✅ **Encrypted storage in Docker**
- ✅ **No plain text in containers**
- ✅ **Automatic key rotation support**

---

## ☁️ **Method 3: Cloud Secret Management**

### **AWS Secrets Manager:**
```python
import boto3
import json

def load_aws_secrets():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='mcp-hub/api-keys')
    secrets = json.loads(response['SecretString'])
    
    for key, value in secrets.items():
        os.environ[key] = value
```

### **Azure Key Vault:**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def load_azure_secrets():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    
    secrets = {
        'OPENAI_API_KEY': client.get_secret("openai-key").value,
        'GOOGLE_API_KEY': client.get_secret("google-key").value,
    }
    
    for key, value in secrets.items():
        os.environ[key] = value
```

### **Google Secret Manager:**
```python
from google.cloud import secretmanager

def load_gcp_secrets():
    client = secretmanager.SecretManagerServiceClient()
    
    secrets = {
        'OPENAI_API_KEY': client.access_secret_version(
            name="projects/your-project/secrets/openai-key/versions/latest"
        ).payload.data.decode('UTF-8'),
        'GOOGLE_API_KEY': client.access_secret_version(
            name="projects/your-project/secrets/google-key/versions/latest"
        ).payload.data.decode('UTF-8'),
    }
    
    for key, value in secrets.items():
        os.environ[key] = value
```

---

## 🔄 **Method 4: Environment Variable Encryption**

### **Setup:**
```bash
# Create encrypted environment file
echo "OPENAI_API_KEY=your-key" | gpg --symmetric --cipher-algo AES256 > .env.gpg

# Decrypt and load
gpg --decrypt .env.gpg | source /dev/stdin
```

### **Automated Loading:**
```bash
#!/bin/bash
# load_encrypted_env.sh

# Decrypt and load environment variables
gpg --decrypt .env.gpg | while read line; do
    export "$line"
done

# Run application
./run.sh
```

---

## 🏗️ **Method 5: Kubernetes Secrets**

### **Create Kubernetes Secret:**
```bash
# Create secret from file
kubectl create secret generic mcp-api-keys \
  --from-literal=OPENAI_API_KEY="your-key" \
  --from-literal=GOOGLE_API_KEY="your-key"

# Or from encrypted file
kubectl create secret generic mcp-api-keys \
  --from-file=api-keys.json
```

### **Deployment Configuration:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-hub
spec:
  template:
    spec:
      containers:
      - name: mcp-hub
        image: mcp-hub:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-api-keys
              key: OPENAI_API_KEY
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-api-keys
              key: GOOGLE_API_KEY
```

---

## 🛠️ **Implementation in MCP Hub**

### **Update run.sh for encrypted keys:**
```bash
#!/bin/bash

# Load encrypted keys if available
if [ -f "secure_key_manager.py" ]; then
    python secure_key_manager.py load
fi

# Continue with normal startup
source venv/bin/activate
streamlit run app.py
```

### **Update app.py for key loading:**
```python
# Add to app.py
def load_encrypted_keys():
    """Load encrypted API keys if available"""
    try:
        from secure_key_manager import load_encrypted_keys_interactive
        return load_encrypted_keys_interactive()
    except ImportError:
        return False

# Call in main function
if __name__ == "__main__":
    load_encrypted_keys()
    main()
```

---

## 🔒 **Security Best Practices**

### **1. Key Rotation:**
```bash
# Rotate keys regularly
python secure_key_manager.py setup  # Re-encrypt with new keys
```

### **2. Access Control:**
```bash
# Restrict file permissions
chmod 600 .encrypted_keys
chmod 600 .key_salt
```

### **3. Audit Logging:**
```python
import logging

def log_key_access(key_name):
    logging.info(f"API key {key_name} accessed at {datetime.now()}")
```

### **4. Environment Separation:**
```bash
# Different keys for different environments
export MCP_ENV="production"
python secure_key_manager.py setup  # Creates .encrypted_keys.production
```

---

## 🚨 **Security Checklist**

### **Before Deployment:**
- [ ] **No plain text API keys** in code or config files
- [ ] **Encrypted key storage** implemented
- [ ] **Master password** set and secured
- [ ] **File permissions** restricted (600)
- [ ] **Key rotation** process established
- [ ] **Access logging** enabled
- [ ] **Backup strategy** for encrypted keys

### **Production Deployment:**
- [ ] **Cloud secret management** configured
- [ ] **Container secrets** properly mounted
- [ ] **Network encryption** enabled
- [ ] **Access controls** implemented
- [ ] **Monitoring** and alerting setup

---

## 📚 **Quick Reference**

### **Local Development:**
```bash
python secure_key_manager.py setup
python secure_key_manager.py load
./run.sh
```

### **Docker Production:**
```bash
export MCP_MASTER_KEY="secure-password"
python docker_secure_setup.py setup
docker-compose up -d
```

### **Cloud Deployment:**
```bash
# Set up cloud secret management
# Update deployment configuration
# Deploy with encrypted keys
```

---

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Failed to decrypt keys"**
   - Check master password
   - Verify salt file exists
   - Ensure proper file permissions

2. **"Docker secret not found"**
   - Verify secret exists: `docker secret ls`
   - Check secret name matches
   - Ensure MCP_MASTER_KEY is set

3. **"Environment variables not set"**
   - Check if keys were loaded successfully
   - Verify key names match
   - Test with `echo $OPENAI_API_KEY`

### **Recovery:**
```bash
# Backup encrypted keys
cp .encrypted_keys .encrypted_keys.backup

# Restore from backup
cp .encrypted_keys.backup .encrypted_keys
```

---

**🔐 Your API keys are now secure! Choose the method that best fits your deployment needs.**
