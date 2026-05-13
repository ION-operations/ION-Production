# Router & Log-Sentinels API Server - Deployment Guide

**Version:** 1.0.0  
**Date:** 2025-01-27

---

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn router_api_server.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# View API docs
open http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build image
docker build -t router-api-server:1.0.0 .

# Run container
docker run -d \
  --name router-api-server \
  -p 8000:8000 \
  -e COMMAND_SERVER_URL=http://localhost:5001 \
  router-api-server:1.0.0

# Or use docker-compose
docker-compose up -d
```

---

## Prerequisites

- **Python:** 3.11+
- **Command Server:** Running on port 5001 (or configured URL)
- **MCP Server:** Accessible via Command Server
- **AIM-OS Systems:** CMC, VIF, SEG, HHNI, TCS, APOE (via MCP)

---

## Installation

### From Source

```bash
cd packages/router_api_server
pip install -r requirements.txt
```

### From Docker

```bash
docker pull router-api-server:1.0.0
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMMAND_SERVER_URL` | `http://localhost:5001` | Command Server HTTP endpoint |
| `PYTHONPATH` | `/app` | Python path for imports |
| `LOG_LEVEL` | `INFO` | Logging level |

### Configuration File (Future)

```yaml
# config.yaml
command_server:
  url: http://localhost:5001
  timeout: 30
  retries: 3

router:
  cache_ttl: 300
  max_proposals: 10

log_sentinels:
  scout_timeout: 700
  forensics_timeout: 8000
  max_parallel_forensics: 2
```

---

## Running the Server

### Development Mode

```bash
uvicorn router_api_server.main:app --reload
```

### Production Mode

```bash
uvicorn router_api_server.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### With Gunicorn (Production)

```bash
gunicorn router_api_server.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Health Checks

### Basic Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "router-log-sentinels-api-server",
  "version": "1.0.0"
}
```

### Detailed Health Check (Future)

```bash
curl http://localhost:8000/health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "service": "router-log-sentinels-api-server",
  "version": "1.0.0",
  "components": {
    "mcp_client": "connected",
    "router_service": "ready",
    "log_sentinels_service": "ready"
  },
  "uptime": 3600,
  "requests": {
    "total": 1000,
    "success": 950,
    "errors": 50
  }
}
```

---

## Monitoring

### Logs

Logs are written to stdout/stderr:

```bash
# Docker
docker logs -f router-api-server

# Kubernetes
kubectl logs -f deployment/router-api-server
```

### Metrics (Future)

Prometheus metrics endpoint (future):

```bash
curl http://localhost:8000/metrics
```

### APM Integration (Future)

- **New Relic:** APM agent
- **Datadog:** APM agent
- **Sentry:** Error tracking

---

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```bash
# Instance 1
uvicorn router_api_server.main:app --port 8000

# Instance 2
uvicorn router_api_server.main:app --port 8001

# Instance 3
uvicorn router_api_server.main:app --port 8002
```

### Kubernetes Scaling

```bash
# Scale deployment
kubectl scale deployment router-api-server --replicas=5

# Auto-scaling (HPA)
kubectl autoscale deployment router-api-server \
  --min=3 \
  --max=10 \
  --cpu-percent=70
```

---

## Security

### Authentication (Future)

Add API key authentication:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### HTTPS/TLS

Use reverse proxy (nginx, Traefik) for TLS termination:

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Rate Limiting (Future)

Add rate limiting middleware:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/router/tools")
@limiter.limit("10/minute")
async def get_tools(request: Request):
    ...
```

---

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration
cp config.yaml config.yaml.backup

# Restore configuration
cp config.yaml.backup config.yaml
```

### State Backup

API server is stateless - no persistent state to backup.

### Log Archival

```bash
# Archive logs
tar -czf logs-$(date +%Y%m%d).tar.gz logs/

# Restore logs
tar -xzf logs-20250127.tar.gz
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi

# Check port availability
netstat -an | grep 8000
```

### Connection Issues

```bash
# Test Command Server
curl http://localhost:5001/mcp/execute

# Check MCP client
python -c "from router_api_server.mcp_client import MCPClient; print('OK')"
```

### Performance Issues

```bash
# Check CPU/memory
top -p $(pgrep -f uvicorn)

# Check logs for errors
tail -f logs/app.log | grep ERROR

# Profile requests
python -m cProfile -o profile.stats router_api_server/main.py
```

---

## Upgrading

### Version Upgrade

```bash
# Pull latest code
git pull

# Install new dependencies
pip install -r requirements.txt --upgrade

# Restart server
systemctl restart router-api-server
# or
docker-compose restart router-api-server
```

### Rollback

```bash
# Revert to previous version
git checkout previous-version

# Restart server
systemctl restart router-api-server
```

---

## Support

- **Documentation:** See `API_DOCUMENTATION.md` and `README.md`
- **Tests:** See `tests/` directory
- **Issues:** Report issues via GitHub Issues

---

## References

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Uvicorn Documentation:** https://www.uvicorn.org/
- **Docker Documentation:** https://docs.docker.com/
- **Kubernetes Documentation:** https://kubernetes.io/docs/

