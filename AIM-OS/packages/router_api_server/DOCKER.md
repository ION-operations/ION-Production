# Router & Log-Sentinels API Server - Docker Configuration

**Version:** 1.0.0  
**Date:** 2025-01-27

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "router_api_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  router-api-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - COMMAND_SERVER_URL=http://command-server:5001
      - PYTHONPATH=/app
    volumes:
      - ./packages:/app/packages
    depends_on:
      - command-server
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  command-server:
    # Command Server configuration (if needed)
    image: command-server:latest
    ports:
      - "5001:5001"
    restart: unless-stopped
```

---

## Building and Running

### Build Docker Image

```bash
cd packages/router_api_server
docker build -t router-api-server:1.0.0 .
```

### Run Docker Container

```bash
docker run -d \
  --name router-api-server \
  -p 8000:8000 \
  -e COMMAND_SERVER_URL=http://localhost:5001 \
  router-api-server:1.0.0
```

### Run with Docker Compose

```bash
cd packages/router_api_server
docker-compose up -d
```

### View Logs

```bash
docker logs -f router-api-server
```

### Stop Container

```bash
docker stop router-api-server
docker rm router-api-server
```

---

## Environment Variables

- `COMMAND_SERVER_URL` (default: `http://localhost:5001`): Command Server HTTP endpoint
- `PYTHONPATH` (default: `/app`): Python path for imports
- `LOG_LEVEL` (default: `INFO`): Logging level

---

## Production Deployment

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: router-api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: router-api-server
  template:
    metadata:
      labels:
        app: router-api-server
    spec:
      containers:
      - name: router-api-server
        image: router-api-server:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: COMMAND_SERVER_URL
          value: "http://command-server:5001"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: router-api-server
spec:
  selector:
    app: router-api-server
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

---

## Health Checks

The API server includes a health check endpoint at `/health`:

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

---

## Monitoring

### Prometheus Metrics (Future)

```python
from prometheus_client import Counter, Histogram

request_count = Counter('router_api_requests_total', 'Total requests')
request_duration = Histogram('router_api_request_duration_seconds', 'Request duration')
```

### Logging

Logs are written to stdout/stderr and can be collected by:
- Docker logs
- Kubernetes logs
- Log aggregation services (ELK, Loki, etc.)

---

## Security Considerations

1. **Authentication:** Add API key or OAuth 2.0 authentication
2. **HTTPS:** Use TLS/SSL in production
3. **Rate Limiting:** Implement rate limiting per IP/API key
4. **Input Validation:** All inputs validated via Pydantic schemas
5. **CORS:** Configure CORS for production domains only

---

## Scaling

### Horizontal Scaling

- Run multiple instances behind a load balancer
- Use Kubernetes HPA (Horizontal Pod Autoscaler)
- Scale based on CPU/memory metrics

### Vertical Scaling

- Increase container resources (CPU/memory)
- Optimize Python code and dependencies

---

## Backup and Recovery

- **Configuration:** Store in version control
- **Logs:** Archive logs regularly
- **State:** API server is stateless (no persistent state)

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs router-api-server

# Check health
curl http://localhost:8000/health

# Check environment variables
docker exec router-api-server env
```

### Connection Issues

```bash
# Test Command Server connection
curl http://localhost:5001/mcp/execute

# Check network connectivity
docker exec router-api-server ping command-server
```

---

## References

- **Docker Documentation:** https://docs.docker.com/
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/
- **Kubernetes Documentation:** https://kubernetes.io/docs/

