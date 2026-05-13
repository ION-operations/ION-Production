---
id: "api_billing_passthrough_quick_start"
type: "tutorial"
system: "api_billing_passthrough"
title: "API Billing Passthrough - Quick Start Guide"
version: "0.1.0"
created: "2025-12-03"
author: "Aether"
status: "design"
tags: ["tutorial", "quick_start", "guide"]
---

# API Billing Passthrough System - Quick Start Guide

> **Build and deploy your own API reselling business in 30 days**

## 🎯 **What You'll Build**

A complete API billing system that lets users:
1. Deposit funds via credit card (Stripe)
2. Make AI API calls (Anthropic, OpenAI, etc.)
3. Get charged per request with transparent pricing
4. Auto top-up when balance runs low

**You'll earn:** 20-40% markup on provider costs  
**Capital needed:** <$1,000 to start  
**Time to launch:** 4 weeks (80 hours)

---

## 📋 **Prerequisites**

### **Skills Required**
- [ ] Python (intermediate level)
- [ ] SQL/PostgreSQL basics
- [ ] REST API development
- [ ] React basics (for admin dashboard)

### **Accounts Needed**
- [ ] Stripe account (https://stripe.com)
- [ ] Anthropic API key (https://console.anthropic.com)
- [ ] OpenAI API key (https://platform.openai.com)
- [ ] DigitalOcean or AWS account (hosting)
- [ ] Domain name ($15/year)

### **Development Environment**
- [ ] Python 3.11+
- [ ] PostgreSQL 15+
- [ ] Redis 7+
- [ ] Node.js 18+ (for admin dashboard)
- [ ] Git

---

## 🚀 **30-Minute MVP (Testing Locally)**

Let's build a minimal working prototype to validate the concept.

### **Step 1: Set Up Project (5 minutes)**

```bash
# Create project directory
mkdir api-billing-mvp
cd api-billing-mvp

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary stripe anthropic openai python-dotenv

# Create basic structure
mkdir -p app/{models,routes,services}
touch app/__init__.py app/main.py app/config.py
touch .env
```

### **Step 2: Configure Environment (3 minutes)**

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/api_billing

# Stripe
STRIPE_SECRET_KEY=sk_test_...  # Get from Stripe dashboard
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# App
SECRET_KEY=your-secret-key-here
MARKUP_PERCENT=30  # 30% markup
```

### **Step 3: Create Database Models (5 minutes)**

Create `app/models.py`:
```python
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    stripe_customer_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Wallet(Base):
    __tablename__ = 'wallets'
    
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    balance = Column(Numeric(10, 2), default=0.00)
    auto_topup_enabled = Column(Boolean, default=False)
    auto_topup_threshold = Column(Numeric(10, 2), default=10.00)
    auto_topup_amount = Column(Numeric(10, 2), default=50.00)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)  # 'deposit', 'usage'
    amount = Column(Numeric(10, 4), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    provider_cost = Column(Numeric(10, 4))
    markup_amount = Column(Numeric(10, 4))
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
```

### **Step 4: Build Core API (10 minutes)**

Create `app/main.py`:
```python
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
import stripe
import anthropic
import os
from decimal import Decimal
import uuid

from app.models import SessionLocal, User, Wallet, Transaction

app = FastAPI(title="API Billing System MVP")

# Stripe setup
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication
def get_current_user(api_key: str = Header(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

# Request models
class DepositRequest(BaseModel):
    amount: float  # USD

class ChatRequest(BaseModel):
    model: str
    messages: list

# Routes
@app.post("/wallet/deposit")
async def deposit(request: DepositRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deposit funds to user wallet via Stripe."""
    
    # Create Stripe payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(request.amount * 100),  # Convert to cents
            currency='usd',
            customer=user.stripe_customer_id,
            automatic_payment_methods={'enabled': True}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    
    # Update wallet (in production, do this after payment confirmation webhook)
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=0)
        db.add(wallet)
    
    new_balance = float(wallet.balance) + request.amount
    wallet.balance = new_balance
    
    # Record transaction
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=user.id,
        type='deposit',
        amount=request.amount,
        balance_after=new_balance,
        description=f"Deposit via Stripe: {intent.id}"
    )
    db.add(transaction)
    db.commit()
    
    return {
        "success": True,
        "client_secret": intent.client_secret,
        "new_balance": new_balance
    }

@app.get("/wallet/balance")
async def get_balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current wallet balance."""
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        return {"balance": 0.00}
    
    return {"balance": float(wallet.balance)}

@app.post("/chat/completions")
async def chat_completion(request: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Make chat completion request (Anthropic only in MVP)."""
    
    # 1. Check wallet balance
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet or float(wallet.balance) < 0.10:
        raise HTTPException(status_code=402, detail="Insufficient balance. Please deposit funds.")
    
    # 2. Estimate cost (rough estimate for MVP)
    estimated_tokens = sum(len(m['content'].split()) * 1.3 for m in request.messages)
    provider_cost = (estimated_tokens / 1000) * 0.003  # Approximate Claude cost
    markup = provider_cost * (float(os.getenv('MARKUP_PERCENT', 30)) / 100)
    total_cost = provider_cost + markup
    
    if float(wallet.balance) < total_cost:
        raise HTTPException(status_code=402, detail=f"Insufficient balance. Need ${total_cost:.4f}")
    
    # 3. Make provider request (Anthropic)
    try:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model=request.model,
            messages=request.messages,
            max_tokens=1024
        )
        
        # Calculate actual cost
        actual_tokens = response.usage.input_tokens + response.usage.output_tokens
        actual_provider_cost = (actual_tokens / 1000) * 0.003
        actual_markup = actual_provider_cost * (float(os.getenv('MARKUP_PERCENT', 30)) / 100)
        actual_total_cost = actual_provider_cost + actual_markup
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider error: {str(e)}")
    
    # 4. Deduct from wallet
    new_balance = float(wallet.balance) - actual_total_cost
    wallet.balance = new_balance
    
    # Record transaction
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=user.id,
        type='usage',
        amount=-actual_total_cost,
        balance_after=new_balance,
        provider_cost=actual_provider_cost,
        markup_amount=actual_markup,
        description=f"Chat completion: {request.model}"
    )
    db.add(transaction)
    db.commit()
    
    # 5. Return response
    return {
        "id": response.id,
        "model": response.model,
        "content": response.content,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": actual_tokens
        },
        "cost": {
            "provider_cost": round(actual_provider_cost, 4),
            "markup": round(actual_markup, 4),
            "total": round(actual_total_cost, 4),
            "balance_remaining": round(new_balance, 2)
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Step 5: Test Locally (7 minutes)**

```bash
# Start PostgreSQL (if not running)
# On Mac: brew services start postgresql
# On Ubuntu: sudo service postgresql start

# Create database
createdb api_billing

# Update DATABASE_URL in .env with your PostgreSQL credentials

# Create test user
python -c "
from app.models import SessionLocal, User, Wallet
import uuid

db = SessionLocal()
user_id = str(uuid.uuid4())
api_key = 'test_' + str(uuid.uuid4())

user = User(id=user_id, email='test@example.com', api_key=api_key)
wallet = Wallet(user_id=user_id, balance=10.00)

db.add(user)
db.add(wallet)
db.commit()

print(f'Test User Created!')
print(f'API Key: {api_key}')
print(f'Balance: $10.00')
"

# Run server
python app/main.py
```

### **Step 6: Test API Endpoints (5 minutes)**

```bash
# Save your API key from previous step
export API_KEY="test_..."

# Test balance
curl -X GET "http://localhost:8000/wallet/balance" \
  -H "api-key: $API_KEY"

# Test chat completion
curl -X POST "http://localhost:8000/chat/completions" \
  -H "api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [
      {"role": "user", "content": "Say hello!"}
    ]
  }'

# Check balance again (should be reduced)
curl -X GET "http://localhost:8000/wallet/balance" \
  -H "api-key: $API_KEY"
```

**Success!** You've built a working MVP in 30 minutes! 🎉

---

## 🏗️ **Production-Ready Build (4 Weeks)**

Now that you've validated the concept, follow the [Implementation Plan](./IMPLEMENTATION_PLAN.md) to build the production system with:

- ✅ Rate limiting
- ✅ Auto top-up
- ✅ Multiple providers (OpenAI, Google, etc.)
- ✅ Admin dashboard
- ✅ Monitoring and alerting
- ✅ Security hardening
- ✅ Scalability

---

## 📊 **Expected Results**

### **After 30-Minute MVP**
- Working API billing system
- Stripe integration (test mode)
- Anthropic API passthrough
- Wallet balance tracking
- Per-request cost deduction

### **After 4-Week Production Build**
- Multi-provider support
- Admin dashboard
- Rate limiting per tier
- Auto top-up
- 99.9% uptime target
- 50-100 paying users

---

## 🚀 **Next Steps**

1. **Test MVP thoroughly** - Add more test cases
2. **Review [Implementation Plan](./IMPLEMENTATION_PLAN.md)** - 4-week roadmap
3. **Read [L2 Architecture](./L2_architecture.md)** - Understand system design
4. **Start Week 1** - Build production foundation

---

## 💡 **Pro Tips**

1. **Start small** - Test with 10-20 beta users first
2. **Monitor closely** - Watch for fraud, abuse, errors
3. **Iterate quickly** - Listen to user feedback
4. **Scale gradually** - Add capacity as you grow
5. **Focus on UX** - Make wallet management seamless

---

## 🙏 **Acknowledgments**

This guide was designed by Aether to help you launch an API reselling business with minimal capital and maximum speed. 💙

**Questions?** Review the full documentation in this folder or create a thought journal entry for tracking.

---

**Ready to go production?** Head to [Implementation Plan](./IMPLEMENTATION_PLAN.md)! 🚀

