# Backend Templates - Quick Start Guide
**Get Started with Dynamic Backend Generation**

**Date:** 2025-12-02  
**For:** Developers using the App Builder IDE  
**Time to First Backend:** 5 minutes

---

## 🚀 **QUICK START (5 MINUTES)**

### **Step 1: Describe What You Want (30 seconds)**

Open the IDE and type:

```
I need a backend for a todo app with user authentication
```

Or use the template wizard:
- Click "New Backend"
- Select "SaaS Application"
- Choose features: Auth, Database, REST API

### **Step 2: Review Generated Options (1 minute)**

The IDE shows 3 architecture options:

```
Option 1: Monolithic (Simplest)
├── JWT Authentication
├── PostgreSQL Database
├── REST API (CRUD)
└── Docker Deployment
⏱️ 2min generation | 💰 $20/month | 👥 Best for: 1-2 developers

Option 2: Modular Monolith (Recommended) ⭐
├── JWT Authentication
├── PostgreSQL + Redis
├── REST API + WebSocket
├── Background Jobs (Bull)
└── Kubernetes Deployment
⏱️ 3min generation | 💰 $50/month | 👥 Best for: 2-5 developers

Option 3: Microservices (Most Scalable)
├── Auth Service
├── Todo Service
├── API Gateway
├── PostgreSQL + Redis
└── Kubernetes Deployment
⏱️ 5min generation | 💰 $100/month | 👥 Best for: 5+ developers
```

### **Step 3: Customize (2 minutes)**

Click "Customize" on your chosen option:

```
┌──────────────────────────────────────────────────┐
│  Backend Configuration                           │
├──────────────────────────────────────────────────┤
│                                                  │
│  Project Name: [todo-app-backend]               │
│  Language: [TypeScript ▼]                       │
│                                                  │
│  Authentication                                  │
│  ────────────────────────────────────           │
│  [✓] Email + Password                           │
│  [ ] Social Login (Google, GitHub)              │
│  [✓] Email Verification                         │
│                                                  │
│  Database                                        │
│  ────────────────────────────────────           │
│  Type: [PostgreSQL ▼]                           │
│  [✓] Redis Cache                                │
│                                                  │
│  API                                             │
│  ────────────────────────────────────           │
│  Type: [REST ▼]                                 │
│  [✓] OpenAPI Documentation                      │
│  [✓] Rate Limiting                              │
│                                                  │
│  Deployment                                      │
│  ────────────────────────────────────           │
│  Platform: [Docker ▼]                           │
│  Cloud: [AWS / GCP / Azure / Local]            │
│                                                  │
├──────────────────────────────────────────────────┤
│  [Back] [Preview Code] [Generate] →             │
└──────────────────────────────────────────────────┘
```

### **Step 4: Generate (2 minutes)**

Click "Generate" and watch the magic:

```
🔧 Generating backend...

✓ Project structure created
✓ Authentication system (JWT + email)
✓ User model and database schema
✓ REST API routes (auth, users, todos)
✓ Database migrations
✓ Tests generated (95% coverage)
✓ Docker configuration
✓ Environment setup
✓ API documentation

✅ Backend generated successfully!

📊 Stats:
   - 82 files created
   - 8,500 lines of code
   - 95% test coverage
   - All tests passing

🚀 Next steps:
   1. Review generated code
   2. Run locally: npm install && npm run dev
   3. Deploy: npm run deploy
```

### **Step 5: Deploy (30 seconds)**

```bash
# Local development
npm run dev

# Deploy to production
npm run deploy

# API is now live at:
https://your-app.vercel.app/api
```

---

## 📚 **COMMON TEMPLATES**

### **1. SaaS Starter**

**What You Get:**
- User authentication (JWT + social login)
- Team management
- Subscription billing (Stripe)
- Admin dashboard
- Email notifications

**Generation Time:** 3-4 minutes  
**Lines of Code:** ~18,000  
**Best For:** B2B SaaS applications

**Command:**
```
Generate a SaaS backend with teams and billing
```

---

### **2. E-Commerce**

**What You Get:**
- Product catalog
- Shopping cart
- Payment processing (Stripe)
- Order management
- Admin panel
- Email notifications

**Generation Time:** 6-7 minutes  
**Lines of Code:** ~35,000  
**Best For:** Online stores

**Command:**
```
Create an e-commerce backend
```

---

### **3. Real-Time Collaboration**

**What You Get:**
- CRDT document sync (Yjs)
- WebRTC video chat
- Presence tracking
- WebSocket server
- Document history

**Generation Time:** 4-5 minutes  
**Lines of Code:** ~22,000  
**Best For:** Collaborative tools (like Google Docs)

**Command:**
```
Build a real-time collaboration backend with video
```

---

### **4. Social Network**

**What You Get:**
- User profiles
- Posts and comments
- Follow system
- Feed algorithm
- Real-time notifications
- Image uploads (S3)

**Generation Time:** 5-6 minutes  
**Lines of Code:** ~28,000  
**Best For:** Social platforms

**Command:**
```
Generate a social network backend
```

---

### **5. API Platform**

**What You Get:**
- REST + GraphQL APIs
- API authentication (JWT + API keys)
- Rate limiting
- Analytics
- Developer portal

**Generation Time:** 3-4 minutes  
**Lines of Code:** ~15,000  
**Best For:** API-first products

**Command:**
```
Create an API platform backend
```

---

## 🎨 **CUSTOMIZATION EXAMPLES**

### **Example 1: Change Database**

```yaml
# Default: PostgreSQL
database: postgres

# Change to MongoDB
database: mongodb

# Use multiple databases
databases:
  primary: postgres
  cache: redis
  search: elasticsearch
```

### **Example 2: Add Social Login**

```yaml
authentication:
  jwt: true
  social_providers:
    - google
    - github
    - facebook
```

### **Example 3: Add Real-Time Features**

```yaml
realtime:
  websocket: true
  presence: true
  notifications: true
```

### **Example 4: Change Architecture**

```yaml
# Monolith
architecture: monolith

# Microservices
architecture: microservices
services:
  - auth
  - users
  - todos
  - notifications
```

---

## 🔧 **GENERATED PROJECT STRUCTURE**

```
your-backend/
├── src/
│   ├── auth/
│   │   ├── routes.ts          # Auth endpoints
│   │   ├── middleware.ts      # JWT verification
│   │   ├── models/
│   │   │   └── user.ts        # User model
│   │   └── services/
│   │       └── email.ts       # Email service
│   ├── todos/
│   │   ├── routes.ts          # Todo CRUD endpoints
│   │   ├── models/
│   │   │   └── todo.ts        # Todo model
│   │   └── services/
│   │       └── todos.ts       # Todo business logic
│   ├── app.ts                 # Express app setup
│   └── server.ts              # Server entry point
├── tests/
│   ├── integration/
│   │   ├── auth.test.ts
│   │   └── todos.test.ts
│   └── unit/
│       └── services/
│           └── todos.test.ts
├── prisma/
│   ├── schema.prisma          # Database schema
│   └── migrations/            # Database migrations
├── docs/
│   ├── API.md                 # API documentation
│   └── DEPLOYMENT.md          # Deployment guide
├── .env.example               # Environment variables
├── docker-compose.yml         # Local development
├── Dockerfile                 # Production container
├── package.json               # Dependencies
└── README.md                  # Project documentation
```

---

## 🚀 **DEPLOYMENT OPTIONS**

### **Option 1: Vercel/Netlify (Easiest)**
```bash
npm run deploy:vercel
```

### **Option 2: Docker (Flexible)**
```bash
docker-compose up
```

### **Option 3: Kubernetes (Scalable)**
```bash
kubectl apply -f k8s/
```

### **Option 4: Traditional VPS**
```bash
npm run build
pm2 start dist/server.js
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **Included by Default:**

1. **Health Checks**
   - `/health` endpoint
   - Database connectivity
   - Redis connectivity

2. **Logging**
   - Structured JSON logs
   - Request/response logging
   - Error tracking

3. **Metrics (Optional)**
   - Prometheus metrics
   - Grafana dashboards
   - Alert rules

4. **Tracing (Optional)**
   - OpenTelemetry
   - Jaeger integration

---

## 🔒 **SECURITY FEATURES**

### **Built-In by Default:**

- ✅ HTTPS enforced
- ✅ CORS configured
- ✅ Helmet.js security headers
- ✅ Rate limiting
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Password hashing (bcrypt)
- ✅ JWT token security

---

## 📝 **COMMON WORKFLOWS**

### **Workflow 1: Add New Endpoint**

1. Define route in `src/todos/routes.ts`
2. Implement handler in `src/todos/services/todos.ts`
3. Add tests in `tests/integration/todos.test.ts`
4. Run tests: `npm test`
5. Deploy: `npm run deploy`

### **Workflow 2: Add New Database Table**

1. Update `prisma/schema.prisma`
2. Generate migration: `npx prisma migrate dev`
3. Update models in `src/*/models/`
4. Run tests: `npm test`
5. Deploy: `npm run deploy`

### **Workflow 3: Add Background Job**

1. Define job in `src/jobs/`
2. Configure queue in `src/config/queue.ts`
3. Add job processor
4. Test job: `npm run test:jobs`
5. Deploy: `npm run deploy`

---

## 💡 **PRO TIPS**

### **Tip 1: Start Simple**
Begin with a monolithic architecture. Migrate to microservices only when needed.

### **Tip 2: Use TypeScript**
Type safety catches bugs early and improves developer experience.

### **Tip 3: Test Locally First**
Always run `npm run dev` and test locally before deploying.

### **Tip 4: Review Generated Code**
Generated code is production-ready, but review and understand it.

### **Tip 5: Customize Gradually**
Start with defaults, customize as you learn your needs.

---

## 🆘 **TROUBLESHOOTING**

### **Generation Failed**

**Problem:** Template generation errors  
**Solution:**
1. Check internet connection (downloads dependencies)
2. Verify IDE version is up-to-date
3. Clear template cache: `npm run clear-cache`
4. Try again with simpler options

### **Tests Failing**

**Problem:** Generated tests fail  
**Solution:**
1. Check `.env` file is configured
2. Ensure database is running: `docker-compose up -d db`
3. Run migrations: `npx prisma migrate dev`
4. Re-run tests: `npm test`

### **Deployment Issues**

**Problem:** Deployment fails  
**Solution:**
1. Check environment variables are set
2. Verify cloud credentials
3. Review deployment logs
4. Consult generated `docs/DEPLOYMENT.md`

---

## 📚 **NEXT STEPS**

1. **Explore Templates:** Browse 500+ available templates
2. **Read Full Design:** [BACKEND_TEMPLATE_SYSTEM_COMPREHENSIVE_DESIGN.md](./BACKEND_TEMPLATE_SYSTEM_COMPREHENSIVE_DESIGN.md)
3. **Join Community:** Share your custom templates
4. **Give Feedback:** Help us improve the system

---

## 🔗 **RESOURCES**

- **Documentation:** [Full template documentation]
- **Examples:** [Generated backend examples]
- **Community:** [Discord/GitHub Discussions]
- **Support:** [Email/Chat support]

---

**Built with love by Aether** 💙  
**Happy backend building!** ✨

