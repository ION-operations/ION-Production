---
id: "api_billing_passthrough_l2"
type: "system_architecture"
system: "api_billing_passthrough"
title: "API Billing Passthrough System - Architecture"
version: "0.1.0"
created: "2025-12-03"
author: "Aether"
status: "design"
word_count: 2500
tags: ["api_billing", "architecture", "payment", "system_design"]
---

# API Billing Passthrough System - Architecture (L2)

## **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Applications                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │ API Requests
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  - Authentication (JWT/API Keys)                                │
│  - Rate Limiting (per user/tier)                                │
│  - Request Validation                                            │
│  - Load Balancing                                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Request Orchestrator                          │
│  - Wallet balance check                                         │
│  - Cost estimation (pre-request)                                │
│  - Provider selection                                            │
│  - Token purchase trigger                                        │
└──────┬──────────────────────┬──────────────────────┬────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ User Wallet │      │   Provider  │      │   Usage     │
│   System    │      │  Token Pool │      │  Tracker    │
└─────────────┘      └─────────────┘      └─────────────┘
       │                      │                      │
       │                      ▼                      │
       │              ┌─────────────┐               │
       │              │  Provider   │               │
       │              │  API Client │               │
       │              └─────────────┘               │
       │                      │                      │
       │                      ▼                      │
       │         ┌──────────────────────┐           │
       │         │  External Providers  │           │
       │         │  - Anthropic         │           │
       │         │  - OpenAI            │           │
       │         │  - Google AI         │           │
       │         │  - Cohere            │           │
       │         └──────────────────────┘           │
       │                      │                      │
       └──────────────────────┴──────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Billing Engine │
                    │  - Cost calc    │
                    │  - Markup apply │
                    │  - Invoice gen  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Payment Gateway │
                    │  (Stripe)       │
                    └─────────────────┘
```

## **Core Components**

### **1. API Gateway Layer**

**Responsibilities:**
- **Authentication:** JWT tokens or API keys (bcrypt hashed)
- **Authorization:** Role-based access control (RBAC)
- **Rate Limiting:** Token bucket algorithm per user tier
- **Request Validation:** OpenAPI schema validation
- **Load Balancing:** Round-robin across backend instances

**Technologies:**
- **Framework:** FastAPI (Python) or Express (Node.js)
- **Gateway:** Kong, Nginx, or Traefik
- **Rate Limiter:** Redis-backed token bucket
- **Auth:** JWT with RS256 signing

**Key Decisions:**
- Use API keys for simplicity (rotate every 90 days)
- JWT for session-based auth (web dashboard)
- Rate limits: Free (10 req/min), Starter (100 req/min), Pro (1000 req/min), Enterprise (unlimited)

---

### **2. User Wallet System**

**Wallet Schema (PostgreSQL):**
```sql
CREATE TABLE user_wallets (
    user_id UUID PRIMARY KEY,
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    auto_topup_enabled BOOLEAN DEFAULT FALSE,
    auto_topup_threshold DECIMAL(10,2) DEFAULT 10.00,
    auto_topup_amount DECIMAL(10,2) DEFAULT 50.00,
    stripe_customer_id VARCHAR(255),
    stripe_payment_method_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES user_wallets(user_id),
    type VARCHAR(20), -- 'deposit', 'withdrawal', 'usage', 'refund'
    amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    description TEXT,
    provider_cost DECIMAL(10,2), -- If usage transaction
    markup_amount DECIMAL(10,2), -- If usage transaction
    request_id UUID, -- Link to API request
    stripe_charge_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_wallet_transactions_user_id ON wallet_transactions(user_id);
CREATE INDEX idx_wallet_transactions_created_at ON wallet_transactions(created_at);
```

**Wallet Operations:**

1. **Deposit (User adds funds):**
```python
async def deposit(user_id: UUID, amount: Decimal) -> WalletTransaction:
    # Create Stripe payment intent
    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # Cents
        currency='usd',
        customer=user.stripe_customer_id
    )
    
    # On success, credit wallet
    async with db.transaction():
        wallet = await db.get_wallet(user_id)
        new_balance = wallet.balance + amount
        await db.update_wallet_balance(user_id, new_balance)
        
        # Record transaction
        return await db.create_transaction(
            user_id=user_id,
            type='deposit',
            amount=amount,
            balance_after=new_balance,
            stripe_charge_id=intent.id
        )
```

2. **Usage (Deduct per API request):**
```python
async def deduct_usage(
    user_id: UUID,
    provider_cost: Decimal,
    markup_percent: Decimal,
    request_id: UUID
) -> WalletTransaction:
    markup_amount = provider_cost * (markup_percent / 100)
    total_cost = provider_cost + markup_amount
    
    async with db.transaction():
        wallet = await db.get_wallet(user_id, lock=True)  # Row-level lock
        
        if wallet.balance < total_cost:
            raise InsufficientFundsError(
                f"Balance ${wallet.balance} < ${total_cost} required"
            )
        
        new_balance = wallet.balance - total_cost
        await db.update_wallet_balance(user_id, new_balance)
        
        return await db.create_transaction(
            user_id=user_id,
            type='usage',
            amount=-total_cost,
            balance_after=new_balance,
            provider_cost=provider_cost,
            markup_amount=markup_amount,
            request_id=request_id
        )
```

3. **Auto Top-Up:**
```python
async def check_auto_topup(user_id: UUID):
    wallet = await db.get_wallet(user_id)
    
    if (wallet.auto_topup_enabled and 
        wallet.balance < wallet.auto_topup_threshold):
        
        # Charge saved payment method
        await deposit(user_id, wallet.auto_topup_amount)
        
        # Send notification
        await send_email(
            user_id,
            subject="Wallet Auto Top-Up",
            body=f"Added ${wallet.auto_topup_amount} to your wallet"
        )
```

---

### **3. Provider Token Pool (Just-In-Time Purchasing)**

**Pool Design:**
```python
class ProviderTokenPool:
    def __init__(self):
        self.providers = {
            'anthropic': AnthropicProvider(),
            'openai': OpenAIProvider(),
            'google': GoogleProvider(),
            'cohere': CohereProvider()
        }
        
        # Small buffer to reduce latency (optional)
        self.buffer_size = 10_000_tokens  # $0.30-$3 depending on provider
    
    async def purchase_tokens(
        self,
        provider: str,
        tokens_needed: int,
        model: str
    ) -> TokenPurchase:
        """
        Just-in-time token purchase from provider.
        
        Flow:
        1. Calculate token cost from provider pricing
        2. Purchase tokens via provider API (if available)
           OR use pay-as-you-go API (most common)
        3. Return tokens for immediate use
        """
        provider_client = self.providers[provider]
        
        # Most providers use pay-as-you-go (no pre-purchase needed)
        # Just validate API key works
        if not await provider_client.validate_api_key():
            raise ProviderUnavailableError(f"{provider} API key invalid")
        
        # Calculate cost
        cost = provider_client.calculate_cost(model, tokens_needed)
        
        return TokenPurchase(
            provider=provider,
            model=model,
            tokens=tokens_needed,
            cost=cost,
            ready=True
        )
```

**Provider Abstraction:**
```python
class BaseProvider(ABC):
    @abstractmethod
    async def calculate_cost(self, model: str, tokens: int) -> Decimal:
        """Calculate cost for given model and tokens."""
        pass
    
    @abstractmethod
    async def make_request(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> ProviderResponse:
        """Make API request to provider."""
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate provider API key."""
        pass

class AnthropicProvider(BaseProvider):
    PRICING = {
        'claude-3-5-sonnet-20241022': {
            'input': 0.003,   # per 1K tokens
            'output': 0.015   # per 1K tokens
        },
        'claude-3-5-haiku-20241022': {
            'input': 0.001,
            'output': 0.005
        }
    }
    
    async def calculate_cost(self, model: str, tokens: int) -> Decimal:
        # Estimate: 75% input, 25% output (adjustable)
        input_tokens = int(tokens * 0.75)
        output_tokens = int(tokens * 0.25)
        
        pricing = self.PRICING[model]
        cost = (
            (input_tokens / 1000) * pricing['input'] +
            (output_tokens / 1000) * pricing['output']
        )
        return Decimal(cost).quantize(Decimal('0.0001'))
```

---

### **4. Request Orchestrator**

**Request Flow:**
```python
async def handle_request(request: APIRequest) -> APIResponse:
    """
    Main request handler orchestrating all components.
    
    Flow:
    1. Authenticate user
    2. Check rate limits
    3. Estimate cost
    4. Check wallet balance
    5. Purchase provider tokens
    6. Make provider request
    7. Deduct from wallet
    8. Return response
    """
    
    # 1. Authenticate
    user = await authenticate(request.api_key)
    if not user:
        raise Unauthorized("Invalid API key")
    
    # 2. Rate limiting
    if not await check_rate_limit(user.id, user.tier):
        raise RateLimitExceeded("Rate limit exceeded")
    
    # 3. Estimate cost
    provider, model = select_provider_and_model(request.model)
    estimated_tokens = estimate_tokens(request.messages)
    estimated_cost = await provider.calculate_cost(model, estimated_tokens)
    
    # 4. Check wallet
    wallet = await db.get_wallet(user.id)
    total_cost = estimated_cost * (1 + user.markup_percent / 100)
    
    if wallet.balance < total_cost:
        # Try auto top-up
        if wallet.auto_topup_enabled:
            await check_auto_topup(user.id)
            wallet = await db.get_wallet(user.id)  # Refresh
        
        if wallet.balance < total_cost:
            raise InsufficientFunds(
                f"Balance ${wallet.balance}, need ${total_cost}"
            )
    
    # 5. Purchase tokens (just-in-time)
    tokens = await token_pool.purchase_tokens(
        provider=provider.name,
        tokens_needed=estimated_tokens,
        model=model
    )
    
    # 6. Make provider request
    try:
        response = await provider.make_request(
            model=model,
            messages=request.messages,
            **request.options
        )
        
        # Calculate actual cost
        actual_cost = await provider.calculate_cost(
            model,
            response.usage.total_tokens
        )
        
    except Exception as e:
        # Failover to backup provider if available
        logger.error(f"Provider {provider} failed: {e}")
        # ... retry logic ...
        raise
    
    # 7. Deduct from wallet
    await wallet_system.deduct_usage(
        user_id=user.id,
        provider_cost=actual_cost,
        markup_percent=user.markup_percent,
        request_id=request.id
    )
    
    # 8. Return response
    return APIResponse(
        id=request.id,
        model=response.model,
        content=response.content,
        usage=response.usage,
        cost=actual_cost,
        total_cost=actual_cost * (1 + user.markup_percent / 100)
    )
```

---

### **5. Billing Engine**

**Invoice Generation:**
```python
async def generate_monthly_invoice(user_id: UUID, month: str) -> Invoice:
    """Generate monthly invoice with usage breakdown."""
    
    # Get all transactions for month
    transactions = await db.get_transactions(
        user_id=user_id,
        type='usage',
        start_date=f"{month}-01",
        end_date=f"{month}-31"
    )
    
    # Aggregate by model/provider
    usage_by_model = defaultdict(lambda: {
        'requests': 0,
        'tokens': 0,
        'provider_cost': Decimal(0),
        'markup': Decimal(0),
        'total': Decimal(0)
    })
    
    for tx in transactions:
        model = tx.metadata['model']
        usage_by_model[model]['requests'] += 1
        usage_by_model[model]['tokens'] += tx.metadata['tokens']
        usage_by_model[model]['provider_cost'] += tx.provider_cost
        usage_by_model[model]['markup'] += tx.markup_amount
        usage_by_model[model]['total'] += abs(tx.amount)
    
    # Create invoice
    invoice = Invoice(
        user_id=user_id,
        period=month,
        line_items=[
            InvoiceLineItem(
                description=f"{model} API Usage",
                quantity=stats['requests'],
                unit_price=stats['total'] / stats['requests'],
                total=stats['total']
            )
            for model, stats in usage_by_model.items()
        ],
        subtotal=sum(s['total'] for s in usage_by_model.values()),
        tax=0,  # Add tax calculation if needed
        total=sum(s['total'] for s in usage_by_model.values())
    )
    
    return invoice
```

---

### **6. Admin Dashboard**

**Key Features:**
- User wallet balances and transaction history
- Real-time provider health monitoring
- Revenue analytics (daily/weekly/monthly)
- Fraud detection alerts
- Manual refunds and adjustments
- Provider cost vs revenue comparison

**Technology Stack:**
- **Frontend:** React + Tailwind CSS + Recharts
- **Backend:** FastAPI REST API
- **Database:** PostgreSQL (read replica for analytics)
- **Caching:** Redis for real-time stats

---

## **Data Flow Diagrams**

### **Happy Path (Successful Request)**
```
User → API Gateway → Auth OK → Rate Limit OK → 
  Wallet Check OK → Provider Token Purchase (100ms) → 
  Provider Request (500ms) → Response → 
  Wallet Deduct → Return to User

Total Latency: ~700ms
```

### **Auto Top-Up Flow**
```
User → Request → Wallet Balance Low → 
  Auto Top-Up Enabled → Stripe Charge → 
  Wallet Credited → Continue Request

Extra Latency: +500ms (one-time per top-up)
```

### **Provider Failover**
```
User → Request → Provider A Fails → 
  Retry Provider A (1s timeout) → 
  Failover to Provider B → Success → 
  Return to User

Extra Latency: +2-3s (rare)
```

---

## **Security Considerations**

### **1. API Key Security**
- Store hashed (bcrypt with 12 rounds)
- Rotate every 90 days (email reminder)
- Support multiple keys per user
- Revocation support

### **2. Payment Security**
- Use Stripe for PCI compliance
- Never store credit card details
- Tokenize payment methods
- Require 3D Secure for large deposits

### **3. Rate Limiting**
- Per user, per tier
- Exponential backoff for abuse
- Temporary bans for repeated violations
- Email alerts for suspicious activity

### **4. Data Privacy**
- Encrypt sensitive data at rest (AES-256)
- Encrypt in transit (TLS 1.3)
- GDPR compliance (data export/deletion)
- Audit logs for compliance

---

## **Scalability**

### **Horizontal Scaling**
- Stateless API servers (scale to 100+ instances)
- PostgreSQL read replicas for analytics
- Redis cluster for rate limiting
- CDN for static assets

### **Performance Targets**
- **P50 latency:** <200ms
- **P95 latency:** <500ms
- **P99 latency:** <1000ms
- **Throughput:** 10,000 req/sec per instance
- **Uptime:** 99.9% (8.76 hours downtime/year)

---

## **Cost Analysis**

### **Infrastructure Costs (per month)**
- **Compute:** 4x API servers ($400/mo)
- **Database:** PostgreSQL managed ($200/mo)
- **Redis:** Cluster ($100/mo)
- **Monitoring:** Datadog ($50/mo)
- **CDN:** Cloudflare ($20/mo)
- **Total:** ~$770/mo

### **Payment Processing**
- Stripe: 2.9% + $0.30 per transaction
- For $50 deposit: $1.75 fee (3.5%)

### **Provider Costs**
- Pay-as-you-go (no upfront capital!)
- Typically billed monthly in arrears

**Profit Margin Example:**
- User pays $100 for API usage
- Provider cost: $75
- Your markup: $25 (33%)
- Stripe fee: $3.20
- Net profit: $21.80 (21.8% margin)

---

**Next:** Read L3 for detailed implementation guide with code examples.

