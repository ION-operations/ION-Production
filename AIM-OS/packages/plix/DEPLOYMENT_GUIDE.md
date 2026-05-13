# PLIx Deployment Guide

**Version:** 1.0.0  
**Status:** Production-ready  
**Date:** 2025-01-27

---

## 🚀 **Deployment Overview**

PLIx is ready for production deployment with multiple options:

1. **NPM Package** - For Node.js applications
2. **Docker Container** - For containerized deployments
3. **Kubernetes** - For cloud-native deployments
4. **Standalone Service** - For microservice architecture

---

## 📦 **NPM Package Deployment**

### **Installation**

```bash
npm install @aimos/plix
```

### **Usage**

```typescript
import { PLIXParser, Pipeline } from '@aimos/plix';

const result = await Pipeline.parseAndCompile(plixText);
```

---

## 🐳 **Docker Deployment**

### **Dockerfile**

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist/ ./dist/
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### **Build & Run**

```bash
docker build -t plix:latest .
docker run -p 3000:3000 plix:latest
```

---

## ☸️ **Kubernetes Deployment**

### **Deployment manifest (`k8s/deployment.yaml`)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: plix
spec:
  replicas: 3
  selector:
    matchLabels:
      app: plix
  template:
    metadata:
      labels:
        app: plix
    spec:
      containers:
      - name: plix
        image: plix:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: NODE_ENV
          value: "production"
```

### **Service manifest (`k8s/service.yaml`)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: plix
spec:
  selector:
    app: plix
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Logging
LOG_LEVEL=info
LOG_OUTPUT=console

# AIM-OS Integration
CMC_URL=http://localhost:5000
HHNI_URL=http://localhost:5001
SEG_URL=http://localhost:5002

# Performance
MAX_CONCURRENCY=10
TIMEOUT_MS=30000

# Security
ENABLE_EFFECT_CHECKING=true
DEFAULT_POLICY=standard
```

---

## 📊 **Monitoring**

### **Metrics Endpoint**

```bash
GET /metrics  # Prometheus format
```

### **Health Check**

```bash
GET /health
```

### **Key Metrics**

- `plix_parse_total` - Parse operations
- `plix_compile_total` - Compile operations
- `plix_parse_duration_ms` - Parse latency
- `plix_compile_duration_ms` - Compile latency
- `plix_confidence` - Confidence scores

---

## 🛡️ **Security Hardening**

### **Production Checklist**

- ✅ Enable effect checking
- ✅ Configure capability policies
- ✅ Set confidence thresholds
- ✅ Enable audit logging
- ✅ Use HTTPS for external calls
- ✅ Implement rate limiting
- ✅ Regular security audits

---

## 🔄 **Rollback Procedures**

### **If Deployment Fails:**

1. Check logs: `kubectl logs -l app=plix`
2. Verify health: `curl http://plix/health`
3. Rollback: `kubectl rollout undo deployment/plix`
4. Investigate and fix
5. Redeploy with fix

---

## ✅ **Production Readiness Checklist**

**Before Deploying:**

- [ ] All tests passing (180+ tests)
- [ ] Code coverage >90%
- [ ] Linting passing
- [ ] Security audit complete
- [ ] Performance benchmarks acceptable
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Rollback procedures tested
- [ ] Backup systems in place
- [ ] Incident response plan ready

---

**Status:** ✅ **DEPLOYMENT-READY**  
**Next:** Monitor production, gather feedback, iterate

