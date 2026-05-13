# Lucid Chat - Deployment Guide

**Version:** 0.9.2  
**Last Updated:** 2025-01-27  
**Status:** Production Ready

---

## 📚 **TABLE OF CONTENTS**

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Development Setup](#development-setup)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)
8. [Scaling Considerations](#scaling-considerations)

---

## 1. Prerequisites

### 1.1 System Requirements

**Minimum Requirements:**
- **CPU:** 2 cores, 2.0 GHz
- **RAM:** 4GB
- **Storage:** 10GB free space
- **OS:** Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

**Recommended Requirements:**
- **CPU:** 4 cores, 3.0 GHz
- **RAM:** 8GB
- **Storage:** 50GB free space
- **OS:** Linux (Ubuntu 22.04 LTS) or macOS 12+
- **Network:** Stable internet connection for API calls

**Production Requirements:**
- **CPU:** 8 cores, 3.5 GHz
- **RAM:** 16GB
- **Storage:** 100GB free space
- **OS:** Linux (Ubuntu 22.04 LTS)
- **Database:** PostgreSQL 13+ (optional, for production CMC/HHNI)

---

### 1.2 Software Requirements

**Required:**
- **Node.js:** v18.0.0 or higher
- **Python:** v3.10.0 or higher
- **npm:** v9.0.0 or higher
- **pip:** v21.0.0 or higher
- **Git:** Latest version

**Optional (for production):**
- **Docker:** v20.10+ (for containerization)
- **PostgreSQL:** v13+ (for production database)
- **Redis:** v6.0+ (for caching)

**Verify Installation:**
```bash
node --version  # Should show v18.0.0+
python --version  # Should show Python 3.10.0+
npm --version  # Should show v9.0.0+
pip --version  # Should show v21.0.0+
git --version  # Should show latest
```

---

### 1.3 AIM-OS Dependencies

Lucid Chat requires AIM-OS core systems:

**Required Systems:**
- **CMC (Context Memory Core):** `packages/cmc_service/`
- **HHNI (Hierarchical Hypergraph Neural Index):** `packages/hhni/`
- **MCP Server:** `lucid_mcp_server.py` (86 tools)
- **Command Server:** Cursor extension (localhost:5001)

**Optional Systems:**
- **VIF (Verifiable Intelligence Framework):** `packages/vif/`
- **SEG (Synthesis Engine Graph):** `packages/seg/`
- **APOE (Autonomous Planning & Orchestration Engine):** `packages/apoe/`

**Note:** AIM-OS systems should be in the same repository or accessible via PYTHONPATH.

---

## 2. Installation

### 2.1 Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-username/AIM-OS.git
cd AIM-OS

# Verify repository structure
ls -la
```

---

### 2.2 Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies for Lucid Chat
pip install sentence-transformers>=2.2.0  # For ICIP semantic search
pip install faiss-cpu>=1.7.4  # For FAISS indexing
pip install aiohttp>=3.8.0  # For async web crawling (DEEPSEARCH)

# Verify installation
python -c "import pydantic; print('✅ Pydantic installed')"
python -c "import numpy; print('✅ NumPy installed')"
python -c "import sentence_transformers; print('✅ Sentence Transformers installed')"
python -c "import faiss; print('✅ FAISS installed')"
```

---

### 2.3 Install Node.js Dependencies

```bash
# Navigate to DAC prototype directory
cd ide_orchestration/prototypes/dac

# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0
```

---

### 2.4 Install AIM-OS Packages

```bash
# Install CMC service
cd packages/cmc_service
pip install -e .
cd ../..

# Install HHNI system
cd packages/hhni
pip install -e .
cd ../..

# Install ICIP search
cd packages/icip_search
pip install -e .
cd ../..

# Install DEEPSEARCH
cd packages/deepsearch
pip install -e .
cd ../..

# Install LLM clients
cd packages/llm_client
pip install -e .
cd ../..

# Install API service registry
cd packages/api_service_registry
pip install -e .
cd ../..
```

---

### 2.5 Verify Installation

```bash
# Test Python MCP server
python lucid_mcp_server.py --help

# Test Node.js build
cd ide_orchestration/prototypes/dac
npm run build

# Run tests
npm test
```

---

## 3. Configuration

### 3.1 Environment Variables

Create `.env` file in project root:

```bash
# API Keys (Required)
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key
CEREBRAS_API_KEY=your-cerebras-api-key
OPENAI_API_KEY=your-openai-api-key

# Optional API Keys
PERPLEXITY_API_KEY=your-perplexity-api-key
TAVILY_API_KEY=your-tavily-api-key
MESHY_API_KEY=your-meshy-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
MINIMAX_API_KEY=your-minimax-api-key

# Command Server Configuration
COMMAND_SERVER_URL=http://localhost:5001
COMMAND_SERVER_PORT=5001

# AIM-OS Configuration
CMC_STORAGE_PATH=./mcp_memory
HHNI_INDEX_PATH=./hhni_index
VIF_WITNESS_PATH=./vif_witnesses

# Budget Configuration
DEFAULT_TOKEN_BUDGET=10000
DEFAULT_TIME_BUDGET=60000
DEFAULT_COST_BUDGET=1.0

# Quality Gate Configuration
DEFAULT_CONFIDENCE_THRESHOLD=0.70
DEFAULT_KAPPA_THRESHOLD=0.75
DEFAULT_QUALITY_THRESHOLD=0.80

# Rate Limiting
DEFAULT_RATE_LIMIT=100
DEFAULT_RATE_WINDOW=60000

# Security
API_KEY=your-api-key-here
ENABLE_AUTHENTICATION=true
ENABLE_AUTHORIZATION=true
```

**Load Environment Variables:**
```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-key"

# macOS/Linux
export ANTHROPIC_API_KEY="your-key"

# Or use python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()"
```

---

### 3.2 Command Server Configuration

**For Cursor Extension:**

Create or update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "lucid-mcp": {
      "command": "python",
      "args": [
        "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\lucid_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

**For Standalone Command Server:**

The Command Server is automatically started by the Cursor extension. To run standalone:

```bash
# Start Command Server (runs on localhost:5001)
# This is typically handled by the Cursor extension
# For testing, you can use the standalone server
cd cursor-addon
npm run build
# Command Server starts automatically when extension activates
```

---

### 3.3 AIM-OS System Configuration

**CMC Configuration:**
```python
# CMC uses SQLite by default
# For production, configure PostgreSQL in config/cmc_config.yaml
```

**HHNI Configuration:**
```python
# HHNI uses FAISS for vector indexing
# Configure in config/hhni_config.yaml
```

**VIF Configuration:**
```python
# VIF uses cryptographic witnesses
# Configure in config/vif_config.yaml
```

---

### 3.4 Service Configuration

**LLM Service Configuration:**
```typescript
// Default providers and models
const defaultProviders = {
  anthropic: 'claude-3-5-sonnet-20241022',
  gemini: 'gemini-2.0-flash-exp',
  cerebras: 'llama-3.1-70b'
}
```

**Search Service Configuration:**
```typescript
// Default search providers
const defaultSearchProviders = [
  'deepsearch',
  'perplexity',
  'tavily',
  'icip',
  'web'
]
```

**Budget Configuration:**
```typescript
// Default budget limits
const defaultBudget = {
  tokens: 10000,
  time: 60000, // 1 minute
  cost: 1.0 // $1.00
}
```

**Quality Gate Configuration:**
```typescript
// Default quality thresholds
const defaultQualityGates = {
  confidence: 0.70,
  kappa: 0.75,
  quality: 0.80,
  consistency: 0.85
}
```

---

## 4. Development Setup

### 4.1 Start Development Environment

**Step 1: Start MCP Server**

```bash
# Terminal 1: Start MCP server
python lucid_mcp_server.py

# Should see:
# [AIM-OS-MCP] Initializing LUCID-MCP Server (86 tools)...
# [AIM-OS-MCP] Server ready
```

**Step 2: Start Command Server**

The Command Server is automatically started by the Cursor extension. If running standalone:

```bash
# Terminal 2: Start Command Server (if standalone)
cd cursor-addon
npm run dev
# Command Server starts on http://localhost:5001
```

**Step 3: Start Frontend Development Server**

```bash
# Terminal 3: Start frontend
cd ide_orchestration/prototypes/dac
npm run dev

# Should see:
# VITE v4.4.0  ready in 500 ms
# ➜  Local:   http://localhost:5173/
```

---

### 4.2 Verify Development Setup

**Test MCP Server:**
```bash
# Test MCP tool
curl -X POST http://localhost:5001/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_memory_stats",
    "arguments": {}
  }'
```

**Test Command Server:**
```bash
# Test Command Server health
curl http://localhost:5001/health
```

**Test Frontend:**
```bash
# Open browser
open http://localhost:5173
```

---

### 4.3 Development Workflow

**1. Make Changes:**
```bash
# Edit TypeScript files
code src/services/lucid-chat/...

# Edit Python files
code lucid_mcp_server.py
```

**2. Test Changes:**
```bash
# Run tests
npm test

# Run specific test
npm test -- test_llm_service.test.ts
```

**3. Build:**
```bash
# Build TypeScript
npm run build

# Verify build
ls dist/
```

---

## 5. Production Deployment

### 5.1 Production Checklist

**Before Deployment:**
- [ ] All tests passing (236 tests/benchmarks)
- [ ] Code coverage ≥90%
- [ ] Security audit passed (85% B+)
- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Database configured (if using PostgreSQL)
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backup strategy in place

---

### 5.2 Production Build

**Build Frontend:**
```bash
cd ide_orchestration/prototypes/dac

# Production build
npm run build

# Verify build
ls dist/
```

**Build Python Packages:**
```bash
# Build all packages
pip install -e packages/cmc_service
pip install -e packages/hhni
pip install -e packages/icip_search
pip install -e packages/deepsearch
pip install -e packages/llm_client
pip install -e packages/api_service_registry
```

---

### 5.3 Production Configuration

**Environment Variables (Production):**
```bash
# Use secure environment variable management
# DO NOT commit .env files to repository

# Production API keys (use secure vault)
export ANTHROPIC_API_KEY="prod-key"
export GEMINI_API_KEY="prod-key"
# ... etc

# Production URLs
export COMMAND_SERVER_URL="https://api.yourdomain.com"
export CMC_STORAGE_PATH="/var/aim-os/cmc"
export HHNI_INDEX_PATH="/var/aim-os/hhni"
```

**Security Configuration:**
```bash
# Enable authentication
export ENABLE_AUTHENTICATION=true
export ENABLE_AUTHORIZATION=true

# Use strong API keys
export API_KEY="$(openssl rand -hex 32)"
```

**Database Configuration (Production):**
```yaml
# config/production.yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  database: aim_os_prod
  user: aim_os_user
  password: ${DB_PASSWORD}
```

---

### 5.4 Deployment Options

**Option 1: Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install packages
COPY packages/ ./packages/
RUN pip install -e packages/cmc_service
RUN pip install -e packages/hhni
# ... etc

# Copy application
COPY lucid_mcp_server.py .
COPY .env .

# Expose port
EXPOSE 5001

# Start server
CMD ["python", "lucid_mcp_server.py"]
```

```bash
# Build Docker image
docker build -t lucid-chat:0.9.2 .

# Run container
docker run -d \
  -p 5001:5001 \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
  --name lucid-chat \
  lucid-chat:0.9.2
```

**Option 2: Systemd Service (Linux)**

```ini
# /etc/systemd/system/lucid-chat.service
[Unit]
Description=Lucid Chat MCP Server
After=network.target

[Service]
Type=simple
User=aimos
WorkingDirectory=/opt/aim-os
Environment="PATH=/opt/aim-os/venv/bin"
ExecStart=/opt/aim-os/venv/bin/python lucid_mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable lucid-chat
sudo systemctl start lucid-chat
sudo systemctl status lucid-chat
```

**Option 3: PM2 (Node.js Process Manager)**

```bash
# Install PM2
npm install -g pm2

# Start MCP server with PM2
pm2 start lucid_mcp_server.py --interpreter python3 --name lucid-chat

# Save PM2 configuration
pm2 save

# Setup PM2 startup
pm2 startup
```

---

### 5.5 Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/lucid-chat
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lucid-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. Monitoring & Logging

### 6.1 Logging Configuration

**Python Logging:**
```python
# Configure logging in lucid_mcp_server.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lucid-chat.log'),
        logging.StreamHandler()
    ]
)
```

**TypeScript Logging:**
```typescript
// Use console for development
console.log('Service started')

// Use structured logging for production
import { logger } from './utils/logger'
logger.info('Service started', { service: 'lucid-chat' })
```

---

### 6.2 Monitoring Setup

**Health Check Endpoint:**
```bash
# Health check
curl http://localhost:5001/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "mcp": "running",
    "command_server": "running"
  }
}
```

**Metrics Endpoint:**
```bash
# Get metrics
curl http://localhost:5001/metrics

# Expected response:
{
  "requests": 1000,
  "errors": 5,
  "latency_ms": 150,
  "tokens_used": 50000,
  "cost": 5.0
}
```

---

### 6.3 Error Tracking

**Sentry Integration (Optional):**
```typescript
import * as Sentry from '@sentry/node'

Sentry.init({
  dsn: 'your-sentry-dsn',
  environment: 'production'
})
```

**Custom Error Tracking:**
```typescript
// Track errors in CMC
await storeToCMC({
  type: 'error',
  message: error.message,
  stack: error.stack,
  timestamp: new Date()
}, 'error_log', ['error', 'production'])
```

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue: Command Server Not Starting**

**Symptoms:**
- Port 5001 already in use
- Connection refused errors

**Solutions:**
```bash
# Check if port is in use
# Windows:
netstat -ano | findstr :5001
# macOS/Linux:
lsof -i :5001

# Kill process using port
# Windows:
taskkill /PID <pid> /F
# macOS/Linux:
kill -9 <pid>

# Or change port
export COMMAND_SERVER_PORT=5002
```

**Issue: MCP Server Not Responding**

**Symptoms:**
- MCP tools return errors
- Connection timeout

**Solutions:**
```bash
# Check MCP server is running
ps aux | grep lucid_mcp_server.py

# Check Python path
python -c "import sys; print(sys.path)"

# Verify MCP server can import packages
python -c "from packages.cmc_service import MemoryStore; print('OK')"
```

**Issue: API Keys Not Working**

**Symptoms:**
- Authentication errors
- 401 Unauthorized

**Solutions:**
```bash
# Verify environment variables
echo $ANTHROPIC_API_KEY

# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"

# Check API key format
# Anthropic: sk-ant-...
# Gemini: AIza...
```

**Issue: Dependencies Missing**

**Symptoms:**
- Import errors
- Module not found

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify package installation
pip list | grep sentence-transformers
pip list | grep faiss

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### 7.2 Performance Issues

**Issue: Slow Response Times**

**Solutions:**
```typescript
// Enable caching
const cache = new CacheManager({
  maxSize: 1000,
  defaultTTL: 3600000
})

// Use parallel execution
const results = await Promise.all([
  search1(),
  search2(),
  search3()
])

// Optimize context window
const context = await contextManager.getContext(messages, {
  strategy: 'relevant', // Better than 'recent'
  maxTokens: 4000
})
```

**Issue: High Memory Usage**

**Solutions:**
```typescript
// Limit cache size
const cache = new CacheManager({
  maxSize: 500, // Reduce from 1000
  defaultTTL: 1800000 // Reduce from 3600000
})

// Clear old cache entries
cache.cleanExpired()

// Limit context window
const context = await contextManager.getContext(messages, {
  maxTokens: 2000 // Reduce from 4000
})
```

---

### 7.3 Debugging

**Enable Debug Logging:**
```bash
# Python
export LOG_LEVEL=DEBUG
python lucid_mcp_server.py

# TypeScript
export DEBUG=lucid-chat:*
npm run dev
```

**Check Logs:**
```bash
# Python logs
tail -f lucid-chat.log

# TypeScript logs
# Check browser console or terminal output
```

**Test Individual Components:**
```bash
# Test MCP tool directly
python -c "
from lucid_mcp_server import SimpleMCPServer
server = SimpleMCPServer()
result = server.handle_tools_call('get_memory_stats', {})
print(result)
"

# Test TypeScript service
npm test -- test_llm_service.test.ts
```

---

## 8. Scaling Considerations

### 8.1 Horizontal Scaling

**Load Balancer:**
```nginx
# Nginx load balancer
upstream lucid_chat {
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
}

server {
    location / {
        proxy_pass http://lucid_chat;
    }
}
```

**Multiple Instances:**
```bash
# Start multiple instances
pm2 start lucid_mcp_server.py --name lucid-chat-1 --interpreter python3
pm2 start lucid_mcp_server.py --name lucid-chat-2 --interpreter python3 -- --port 5002
pm2 start lucid_mcp_server.py --name lucid-chat-3 --interpreter python3 -- --port 5003
```

---

### 8.2 Database Scaling

**PostgreSQL for Production:**
```yaml
# Use PostgreSQL for CMC/HHNI in production
database:
  type: postgresql
  connection_pool:
    min: 5
    max: 20
  read_replicas:
    - host: replica1.example.com
    - host: replica2.example.com
```

---

### 8.3 Caching Strategy

**Redis for Distributed Caching:**
```python
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)

# Use Redis for shared cache
cache.set('key', 'value', ttl=3600)
```

---

### 8.4 Resource Limits

**Set Resource Limits:**
```typescript
// Budget limits per user
const userBudget = {
  tokens: 10000,
  time: 60000,
  cost: 1.0
}

// Rate limits per user
const userRateLimit = {
  limit: 100,
  window: 60000
}
```

---

## 9. Security Best Practices

### 9.1 API Key Management

**DO:**
- Store API keys in environment variables
- Use secure vaults (AWS Secrets Manager, HashiCorp Vault)
- Rotate API keys regularly
- Use different keys for dev/staging/production

**DON'T:**
- Commit API keys to repository
- Hardcode API keys in code
- Share API keys in plain text
- Use same keys across environments

---

### 9.2 Authentication

**Enable Authentication:**
```typescript
import { Authentication } from './security/Authentication'

// Always authenticate requests
const result = Authentication.authenticate(apiKey, {
  requireAuth: true,
  apiKey: process.env.API_KEY
})

if (!result.authenticated) {
  throw new Error('Unauthorized')
}
```

---

### 9.3 Input Validation

**Always Validate Input:**
```typescript
import { InputValidator, SecurityValidator } from './validation'

// Validate and sanitize
const validated = InputValidator.validateString(userInput, 'query', {
  minLength: 1,
  maxLength: 1000
})

const sanitized = SecurityValidator.sanitizeString(validated)

// Check for attacks
if (SecurityValidator.detectXSS(sanitized)) {
  throw new Error('XSS detected')
}
```

---

## 10. Backup & Recovery

### 10.1 Backup Strategy

**CMC Data Backup:**
```bash
# Backup CMC SQLite database
cp mcp_memory/cmc.db mcp_memory/cmc.db.backup

# Or use PostgreSQL dump
pg_dump aim_os_cmc > backup_$(date +%Y%m%d).sql
```

**HHNI Index Backup:**
```bash
# Backup FAISS index
cp hhni_index/faiss.index hhni_index/faiss.index.backup
```

---

### 10.2 Recovery

**Restore from Backup:**
```bash
# Restore CMC
cp mcp_memory/cmc.db.backup mcp_memory/cmc.db

# Restore HHNI
cp hhni_index/faiss.index.backup hhni_index/faiss.index

# Restore PostgreSQL
psql aim_os_cmc < backup_20250127.sql
```

---

## 11. Maintenance

### 11.1 Regular Maintenance

**Daily:**
- Check logs for errors
- Monitor API usage
- Check budget limits

**Weekly:**
- Review performance metrics
- Clean old cache entries
- Update dependencies

**Monthly:**
- Security audit
- Performance optimization
- Documentation updates

---

### 11.2 Dependency Updates

```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Node.js dependencies
npm update

# Check for security vulnerabilities
npm audit
pip check
```

---

**Status:** ✅ **COMPLETE**  
**Version:** 0.9.2  
**Last Updated:** 2025-01-27  
**Word Count:** ~1,400 words


