# Economic Router Math: Bandit Objective and Regret Bounds

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Define bandit objective, regret bounds, and update rules for APOE router

---

## 🎯 **OBJECTIVE**

Define economic router math:
1. **Bandit objective:** `J = α·cost + β·latency − γ·p_success`
2. **Regret bounds:** Formal regret analysis
3. **Update rules:** Online learning update rules

---

## 📊 **BANDIT OBJECTIVE**

### **Objective Function**

```
J = α·cost + β·latency − γ·p_success

where:
  - α, β, γ ≥ 0  (weights)
  - cost ∈ ℝ₊  (execution cost)
  - latency ∈ ℝ₊  (execution time)
  - p_success ∈ [0,1]  (success probability)
```

**Goal:** Minimize `J` (lower is better)

### **Component Definitions**

**Cost:**
```
cost = token_cost + api_cost + compute_cost

where:
  - token_cost = tokens_used × token_price
  - api_cost = api_calls × api_price
  - compute_cost = compute_time × compute_price
```

**Latency:**
```
latency = network_latency + compute_time + queue_time
```

**Success Probability:**
```
p_success = P(contract.postconditions_satisfied | plan_execution)
```

---

## 🎲 **MULTI-ARMED BANDIT FORMULATION**

### **Arms (Actions)**

Each arm `a ∈ A` represents a plan execution strategy:
- Different model selection
- Different tool routing
- Different retry strategies
- Different fallback strategies

### **Reward**

```
R(a) = −J(a) = −(α·cost(a) + β·latency(a) − γ·p_success(a))
```

**Goal:** Maximize reward (equivalent to minimizing objective)

### **Expected Reward**

```
E[R(a)] = −(α·E[cost(a)] + β·E[latency(a)] − γ·E[p_success(a)])
```

---

## 📈 **REGRET BOUNDS**

### **Regret Definition**

**Cumulative Regret:**
```
R_T = ∑_{t=1}^T (R(a*) − R(a_t))

where:
  - a* = optimal arm
  - a_t = arm selected at time t
```

**Expected Regret:**
```
E[R_T] = ∑_{t=1}^T (E[R(a*)] − E[R(a_t)])
```

### **Upper Confidence Bound (UCB) Regret Bound**

**UCB Algorithm:**
```
a_t = argmax_{a∈A} (μ̂_a + c·√(log(t) / n_a))

where:
  - μ̂_a = empirical mean reward for arm a
  - n_a = number of times arm a was selected
  - c = exploration constant
```

**Regret Bound:**
```
E[R_T] ≤ O(√(T·log(T)))
```

**For finite arms:**
```
E[R_T] ≤ O(√(T·K·log(T)))

where K = |A| (number of arms)
```

### **Thompson Sampling Regret Bound**

**Thompson Sampling:**
```
Sample θ_a ~ Posterior(θ_a | history)
a_t = argmax_{a∈A} E[R(a) | θ_a]
```

**Regret Bound:**
```
E[R_T] ≤ O(√(T·K·log(T)))
```

---

## 🔄 **UPDATE RULES**

### **Online Learning Update**

**Reward Observation:**
```
After executing arm a_t at time t:
  Observe: cost_t, latency_t, success_t
  Compute: R_t = −(α·cost_t + β·latency_t − γ·success_t)
```

**Empirical Mean Update:**
```
μ̂_a ← (n_a·μ̂_a + R_t) / (n_a + 1)
n_a ← n_a + 1
```

**Variance Update:**
```
σ̂²_a ← (n_a·σ̂²_a + (R_t − μ̂_a)²) / (n_a + 1)
```

### **Confidence Interval Update**

**UCB Confidence:**
```
UCB_a = μ̂_a + c·√(log(t) / n_a)
```

**Thompson Sampling Update:**
```
Posterior(θ_a) ← Prior(θ_a) × Likelihood(R_t | θ_a)
```

### **Weight Adaptation**

**Adaptive Weights:**
```
α_t ← α_{t-1}·exp(−η·cost_t)
β_t ← β_{t-1}·exp(−η·latency_t)
γ_t ← γ_{t-1}·exp(η·success_t)

where η = learning_rate
```

**Normalization:**
```
α_t ← α_t / (α_t + β_t + γ_t)
β_t ← β_t / (α_t + β_t + γ_t)
γ_t ← γ_t / (α_t + β_t + γ_t)
```

---

## 🎯 **ROUTER IMPLEMENTATION**

### **Router Algorithm**

```
function route(intent, context):
  // Step 1: Generate candidate arms
  arms = generate_candidates(intent, context)
  
  // Step 2: Select arm using bandit algorithm
  arm = select_arm(arms, history)
  
  // Step 3: Execute plan with selected arm
  result = execute_plan(intent, arm)
  
  // Step 4: Observe reward
  reward = compute_reward(result)
  
  // Step 5: Update bandit
  update_bandit(arm, reward)
  
  return result
```

### **Arm Selection (UCB)**

```
function select_arm_ucb(arms, history, t):
  best_arm = null
  best_ucb = -∞
  
  for arm in arms:
    μ̂ = history.mean_reward(arm)
    n = history.count(arm)
    ucb = μ̂ + c·√(log(t) / n)
    
    if ucb > best_ucb:
      best_ucb = ucb
      best_arm = arm
  
  return best_arm
```

### **Arm Selection (Thompson Sampling)**

```
function select_arm_thompson(arms, history):
  best_arm = null
  best_sample = -∞
  
  for arm in arms:
    θ = sample_posterior(arm, history)
    expected_reward = E[reward(arm) | θ]
    
    if expected_reward > best_sample:
      best_sample = expected_reward
      best_arm = arm
  
  return best_arm
```

---

## 📊 **PERFORMANCE METRICS**

### **Regret Metrics**

**Cumulative Regret:**
```
R_T = ∑_{t=1}^T (R(a*) − R(a_t))
```

**Average Regret:**
```
R̄_T = R_T / T
```

**Regret Rate:**
```
lim_{T→∞} R_T / T = 0  (sublinear regret)
```

### **Success Metrics**

**Success Rate:**
```
p_success = (# successful executions) / (# total executions)
```

**Cost Efficiency:**
```
cost_per_success = total_cost / (# successful executions)
```

**Latency Efficiency:**
```
latency_per_success = total_latency / (# successful executions)
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Bandit Objective** - Complete
2. ✅ **Regret Bounds** - Complete
3. ✅ **Update Rules** - Complete
4. ⏳ **Implementation** - Link to APOE router

---

**Status:** 📋 **ROUTER MATH SPECIFICATION COMPLETE**  
**Next:** Durable execution research

