---
id: "api_billing_passthrough_l1"
type: "system_overview"
system: "api_billing_passthrough"
title: "API Billing Passthrough System - Overview"
version: "0.1.0"
created: "2025-12-03"
author: "Aether"
status: "design"
word_count: 500
tags: ["api_billing", "payment", "passthrough", "fintech"]
---

# API Billing Passthrough System - Overview (L1)

## **The Problem**

Offering AI API access to users traditionally requires:
- **$10k-$100k+ upfront deposit** with providers (Anthropic, OpenAI, etc.)
- **Cash flow risk:** Pre-purchase tokens that may go unused
- **Inventory management:** Track token balances across providers
- **Pricing complexity:** Markup + usage tracking + billing cycles

This creates massive barrier to entry for API reselling businesses.

## **The Solution: Just-In-Time Token Passthrough**

**Core Concept:** Never hold token inventory. Purchase from provider 100ms before delivering to user.

### **User Flow (3 seconds end-to-end)**
1. User makes API request to your endpoint
2. System checks user's prepaid wallet balance
3. If sufficient balance → Purchase tokens from provider (100ms)
4. Forward request to provider with purchased tokens
5. Return response to user
6. Deduct cost + markup from user's wallet

### **Payment Flow (Prepaid Wallet Model)**
1. User deposits $50-$500 via Stripe
2. Funds held in user's wallet (your Stripe account)
3. Consumed per-request with transparent pricing
4. Auto top-up when balance falls below threshold
5. Email notifications for low balance

### **Provider Integration (Multi-Provider Support)**
```
Your System → [Provider Router] → Anthropic/OpenAI/Google/Cohere
              ↓
         [Token Purchase]
              ↓
         [Usage Tracking]
```

## **Key Components**

### **1. User Wallet System**
- Prepaid balance (Stripe-backed)
- Usage tracking per request
- Auto top-up rules (configurable)
- Balance alerts (email + webhook)
- Refund support

### **2. Provider Token Purchaser**
- Real-time token purchase from providers
- Exponential backoff retry logic
- Provider health monitoring
- Failover to backup providers
- Transaction logging

### **3. Request Router**
- Model-to-provider mapping
- Load balancing across providers
- Rate limiting (per user/tier)
- Request validation
- Response caching (optional)

### **4. Billing Engine**
- Real-time cost calculation
- Configurable markup (20-40%)
- Usage analytics per user
- Invoice generation
- Tax calculation (optional)

### **5. Admin Dashboard**
- User wallet management
- Provider health monitoring
- Revenue analytics
- Fraud detection
- Manual refunds/adjustments

## **Business Model**

### **Pricing Tiers**
- **Free Tier:** $0/month + 40% markup (rate limited)
- **Starter:** $29/month + 30% markup
- **Professional:** $99/month + 25% markup
- **Enterprise:** $499/month + 20% markup + dedicated support

### **Revenue Streams**
1. **Per-token markup:** 20-40% on provider costs
2. **Subscription fees:** $29-$499/month
3. **Float interest:** Earn interest on prepaid balances (Stripe Treasury)

### **Capital Requirements**
- **Initial:** $500-$1000 for provider testing accounts
- **Operating:** <$5000 working capital (covers 100 concurrent users)
- **Scale:** Working capital scales linearly with concurrent requests

## **Risk Mitigation**

1. **Prepaid wallet** → No credit risk
2. **Rate limiting** → Prevent abuse
3. **Provider failover** → 99.9% uptime
4. **Audit trails** → Compliance & debugging
5. **Fraud detection** → Block suspicious patterns

## **Success Metrics**

- **Capital Efficiency:** <$1k capital per $100k annual revenue
- **Latency:** <200ms request-to-response
- **Uptime:** 99.9%+ availability
- **User Satisfaction:** >4.5/5 stars
- **Profit Margin:** 15-25% net after costs

---

**Next:** Read L2 for detailed architecture and implementation guide.

