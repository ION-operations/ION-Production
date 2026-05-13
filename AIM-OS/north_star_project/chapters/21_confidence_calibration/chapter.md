# Chapter 21 - Confidence Calibration

Status: Drafting under intelligent quality gates (tier A)
Mode: Completeness-based writing

## Purpose
- Detail the mathematical calibration of confidence signals (VIF, authority, capability) to keep decisions reliable.
- Describe Bayesian update routines, calibration experiments, and dashboards that track confidence accuracy.
- Provide runnable commands to observe calibration data and adjust confidence.

## Calibration Model

Confidence is treated as a probability distribution updated via Bayes' rule:
```
posterior = prior * likelihood / evidence
```

**Component Details:**

**Prior Distribution:**
- Historical accuracy of the system/persona in similar contexts
- Formula: `prior = Beta(α, β)` where α = successes, β = failures
- Updated after each outcome: `α_new = α + success`, `β_new = β + failure`
- Mean: `E[prior] = α / (α + β)`

**Likelihood Function:**
- Probability of observing current evidence if claim is correct
- Sources: quality gates (SDF-CVF), tests (quartet parity), audits (CAS)
- Formula: `likelihood = P(evidence | claim_true)`
- Combined: `likelihood = ∏ P(gate_i | claim_true)` for all gates i

**Evidence (Normalization):**
- Ensures probabilities sum to 1.0
- Formula: `evidence = prior * likelihood + (1 - prior) * (1 - likelihood)`
- Marginal probability of observing the evidence

**Posterior Distribution:**
- Updated confidence after observing evidence
- Formula: `posterior = (prior * likelihood) / evidence`
- Mean: `E[posterior] = (α + successes) / (α + β + total_observations)`

**Calibration Curves:**
- Map predicted confidence to observed success rates
- Bins: [0.0-0.1], [0.1-0.2], ..., [0.9-1.0]
- For each bin: `calibration = observed_success_rate / predicted_confidence`
- Perfect calibration: calibration = 1.0 for all bins
- Deviations trigger rebalancing via prior updates

## Confidence Types

AIM-OS distinguishes four confidence types to prevent inflation:

**Type 1: Direction Confidence**
- Question: "Is this the RIGHT choice?"
- Example: VIF implementation = 0.95 (clearly serves OBJ-03)
- Context: Strategic alignment

**Type 2: Execution Confidence**
- Question: "Can I DO this successfully?"
- Example: VIF implementation = 0.65 (never built code from docs)
- Context: Technical capability

**Type 3: Autonomous Confidence**
- Question: "Can I do this ALONE without help?"
- Example: VIF implementation = 0.60 (will need questions answered)
- Context: Self-sufficiency

**Type 4: Collaborative Confidence**
- Question: "Can I do this WITH support?"
- Example: VIF implementation = 0.75 (can ask when stuck)
- Context: Team collaboration

**Calibration Model Per Type:**
```python
calibration_model = {
    "documentation_tasks": {
        "bias": -0.05,  # Slightly underconfident
        "accuracy": 0.95  # Usually correct
    },
    "code_tasks": {
        "bias": +0.20,  # OVERCONFIDENT (predicted 0.85, actual 0.65)
        "accuracy": 0.70  # Sometimes struggle
    },
    "organizational_tasks": {
        "bias": 0.00,  # Well calibrated
        "accuracy": 0.90
    }
}

# When making new decision:
raw_confidence = my_intuition()  # 0.85
task_category = classify(task)  # "code_tasks"
calibrated_confidence = raw_confidence - calibration_model[task_category]["bias"]
# 0.85 - 0.20 = 0.65 ← HONEST confidence
```

## Runnable Examples

### Example 1: Read Calibration Metrics
```powershell
# Read current confidence metrics (includes calibration summary)
$metrics = @{ 
    tool='get_consciousness_metrics'; 
    arguments=@{
        include_calibration=$true;
        include_ece=$true
    } 
} | ConvertTo-Json -Depth 6

$result = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $metrics |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

# Display calibration data
Write-Host "ECE: $($result.calibration.ece)"
Write-Host "Brier Score: $($result.calibration.brier_score)"
Write-Host "Calibration Bins:"
$result.calibration.bins | ForEach-Object {
    Write-Host "  [$($_.range)]: Predicted=$($_.predicted), Observed=$($_.observed), Count=$($_.count)"
}
```

### Example 2: Track Confidence Update
```powershell
# Record a confidence update after validation
$update = @{ 
    tool='track_confidence'; 
    arguments=@{ 
        task='Chapter 21 - Confidence Calibration';
        predicted=0.85;
        actual=0.90;
        confidence_type='collaborative';
        task_category='documentation'
    } 
} | ConvertTo-Json -Depth 6

Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $update |
    Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### Example 3: Calculate Calibration Bias
```powershell
# Query confidence history for bias calculation
$history = @{ 
    tool='get_ai_messages'; 
    arguments=@{ 
        content_search='confidence';
        limit=50
    } 
} | ConvertTo-Json -Depth 6

$messages = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $history |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

# Calculate bias per task category
$bias = @{}
$messages | Where-Object { $_.tags.task_category } | Group-Object { $_.tags.task_category } | ForEach-Object {
    $category = $_.Name
    $predictions = $_.Group | ForEach-Object { $_.tags.predicted_confidence }
    $actuals = $_.Group | ForEach-Object { $_.tags.actual_outcome }
    $bias[$category] = ($predictions | Measure-Object -Average).Average - ($actuals | Measure-Object -Average).Average
}

Write-Host "Calibration Bias by Category:"
$bias.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key): $($_.Value)"
}
```

## Calibration Workflow
1. Record prediction (confidence before execution).
2. Run validations (examples, audits, deployments).
3. Compare outcome with prediction; compute calibration error.
4. Update priors and weightings; log results in CAS + SEG.

## Expected Calibration Error (ECE)

ECE measures how well-calibrated probabilistic predictions are:

**Formula:**
```
ECE = Σ (|B_m| / n) * |acc(B_m) - conf(B_m)|
```

Where:
- `B_m`: Bin m containing predictions
- `|B_m|`: Number of predictions in bin m
- `n`: Total number of predictions
- `acc(B_m)`: Actual accuracy in bin m
- `conf(B_m)`: Average predicted confidence in bin m

**Interpretation:**
- ECE = 0.0: Perfect calibration (predicted = actual)
- ECE < 0.05: Well calibrated
- ECE > 0.10: Poor calibration (requires adjustment)

**Binning Strategy:**
- Optimal bin count: `sqrt(n)` where n = number of predictions
- Equal-width bins: [0.0-0.1], [0.1-0.2], ..., [0.9-1.0]
- Equal-frequency bins: Each bin contains equal number of predictions

## Metrics & Dashboards

**Brier Score:**
- Measures accuracy of probabilistic predictions
- Formula: `Brier = (1/n) * Σ (predicted_i - actual_i)²`
- Range: [0.0, 1.0] where 0.0 = perfect, 1.0 = worst
- Decomposes into: `Brier = Calibration + Resolution + Uncertainty`
  - Calibration: How well probabilities match frequencies
  - Resolution: How well predictions distinguish outcomes
  - Uncertainty: Inherent unpredictability

**Calibration Bins:**
- Bucket predictions into bins (e.g., 0.5-0.6, 0.6-0.7, etc.)
- Compare expected vs actual success rates
- Visualize as calibration plot: predicted (x-axis) vs observed (y-axis)
- Perfect calibration: diagonal line (y = x)

**VIF Drift:**
- Monitors changes after calibration updates
- Formula: `drift = |VIF_new - VIF_old|`
- Threshold: drift > 0.10 triggers review
- Tracks: per-system, per-persona, per-task-type

**Confidence Gap Log:**
- Highlights systems consistently over/under confident
- Overconfidence: predicted > actual (bias > 0)
- Underconfidence: predicted < actual (bias < 0)
- Tracks: bias per task category, temporal trends, improvement velocity

## Failure Modes & Mitigations
- **Overconfidence:** tighten gates; require additional evidence; adjust priors.
- **Underconfidence:** encourage more automation; add proof tasks; revisit penalties.
- **Data sparsity:** increase sampling; run synthetic experiments; aggregate across similar contexts.
- **Model drift:** retrain calibration curves; run regression tests.

## Integration
- **VIF:** uses calibrated confidence to gate work; stores updates per chapter/system.
- **CAS:** awareness dashboards display calibration status; anomalies trigger alerts.
- **SDF-CVF:** quality results feed likelihood calculations.
- **APOE/SIS:** improvements proposed when calibration error exceeds thresholds.

## Mathematical Foundations

Confidence calibration in AIM-OS is grounded in Bayesian probability theory and statistical learning. The mathematical framework ensures that confidence signals accurately reflect the true probability of success.

### Bayesian Update Theory

**Bayesian Inference Framework:**
- **Prior Belief:** Initial confidence based on historical performance
- **Evidence:** Observed outcomes from quality gates, tests, audits
- **Posterior Belief:** Updated confidence after observing evidence
- **Conjugate Prior:** Beta distribution for binary outcomes (success/failure)

**Beta Distribution Properties:**
- Parameters: α (successes), β (failures)
- Mean: `E[θ] = α / (α + β)`
- Variance: `Var[θ] = (α × β) / ((α + β)² × (α + β + 1))`
- Mode: `(α - 1) / (α + β - 2)` for α, β > 1
- Conjugate: Beta-Binomial conjugacy enables efficient updates

**Update Rule:**
```
α_new = α_old + successes
β_new = β_old + failures
```

**Confidence Interval:**
- 95% credible interval: `[Beta(α, β).ppf(0.025), Beta(α, β).ppf(0.975)]`
- Provides uncertainty quantification alongside point estimate

### Calibration Theory

**Perfect Calibration Definition:**
A system is perfectly calibrated if, for all confidence levels c:
```
P(success | predicted_confidence = c) = c
```

**Calibration Error:**
- Measures deviation from perfect calibration
- Formula: `CE = E[|predicted - actual|]`
- Decomposes into: systematic bias + random error

**Calibration Curve:**
- Maps predicted confidence to observed success rate
- Perfect calibration: diagonal line (y = x)
- Overconfidence: curve below diagonal
- Underconfidence: curve above diagonal

### Statistical Learning Framework

**Online Learning:**
- Updates calibration model after each outcome
- Exponential moving average: `θ_t = α × θ_{t-1} + (1 - α) × x_t`
- Adaptive learning rate: decreases over time for stability

**Task Category Clustering:**
- Groups similar tasks for bias estimation
- Features: task type, complexity, domain, tools used
- Clustering: k-means or hierarchical clustering
- Bias per cluster: `bias_k = mean(predicted_k - actual_k)`

## Calibration Algorithms

AIM-OS implements several calibration algorithms to maintain accurate confidence signals:

### Algorithm 1: Beta-Binomial Calibration

**Purpose:** Update confidence using Beta-Binomial conjugacy

**Algorithm:**
```python
def beta_binomial_calibration(prior_alpha, prior_beta, successes, failures):
    """
    Update Beta prior with observed outcomes.
    
    Args:
        prior_alpha: Prior α parameter (successes)
        prior_beta: Prior β parameter (failures)
        successes: Observed successes
        failures: Observed failures
    
    Returns:
        Updated (α, β) parameters
    """
    alpha_new = prior_alpha + successes
    beta_new = prior_beta + failures
    return alpha_new, beta_new

# Example usage
alpha, beta = beta_binomial_calibration(α=10, β=2, successes=5, failures=1)
confidence = alpha / (alpha + beta)  # Updated confidence
```

**Properties:**
- Efficient: O(1) update time
- Memory: Stores only (α, β) parameters
- Interpretable: Direct probability interpretation

### Algorithm 2: Platt Scaling

**Purpose:** Calibrate confidence scores using logistic regression

**Algorithm:**
```python
def platt_scaling(raw_scores, labels):
    """
    Calibrate raw confidence scores using Platt scaling.
    
    Args:
        raw_scores: Raw confidence scores [0, 1]
        labels: Binary outcomes (0 = failure, 1 = success)
    
    Returns:
        Calibrated scores
    """
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression
    
    # Fit Platt scaling
    platt = CalibratedClassifierCV(
        LogisticRegression(),
        method='sigmoid',
        cv=5
    )
    platt.fit(raw_scores.reshape(-1, 1), labels)
    
    # Calibrate new scores
    calibrated = platt.predict_proba(raw_scores.reshape(-1, 1))[:, 1]
    return calibrated
```

**Properties:**
- Non-parametric: No distribution assumptions
- Flexible: Adapts to any score distribution
- Requires: Calibration dataset

### Algorithm 3: Isotonic Regression

**Purpose:** Non-parametric calibration using isotonic regression

**Algorithm:**
```python
def isotonic_calibration(raw_scores, labels):
    """
    Calibrate using isotonic regression (piecewise constant).
    
    Args:
        raw_scores: Raw confidence scores [0, 1]
        labels: Binary outcomes (0 = failure, 1 = success)
    
    Returns:
        Calibrated scores
    """
    from sklearn.isotonic import IsotonicRegression
    
    # Fit isotonic regression
    iso = IsotonicRegression(out_of_bounds='clip')
    iso.fit(raw_scores, labels)
    
    # Calibrate new scores
    calibrated = iso.transform(raw_scores)
    return calibrated
```

**Properties:**
- Non-parametric: No distribution assumptions
- Monotonic: Preserves score ordering
- Flexible: Piecewise constant mapping

### Algorithm 4: Temperature Scaling

**Purpose:** Single-parameter calibration for neural network outputs

**Algorithm:**
```python
def temperature_scaling(logits, temperature):
    """
    Calibrate logits using temperature scaling.
    
    Args:
        logits: Raw logits from model
        temperature: Temperature parameter (T > 0)
    
    Returns:
        Calibrated probabilities
    """
    import torch.nn.functional as F
    
    # Apply temperature scaling
    scaled_logits = logits / temperature
    calibrated = F.softmax(scaled_logits, dim=-1)
    return calibrated

# Optimal temperature via cross-validation
def find_optimal_temperature(logits, labels, temp_range=[0.1, 10.0]):
    """
    Find optimal temperature via cross-validation.
    """
    best_temp = 1.0
    best_ece = float('inf')
    
    for temp in np.linspace(temp_range[0], temp_range[1], 100):
        calibrated = temperature_scaling(logits, temp)
        ece = calculate_ece(calibrated, labels)
        if ece < best_ece:
            best_ece = ece
            best_temp = temp
    
    return best_temp
```

**Properties:**
- Simple: Single parameter to tune
- Efficient: O(n) computation
- Effective: Works well for neural networks

## System Architecture

The confidence calibration system integrates with all AIM-OS systems to provide accurate confidence signals:

### Core Components

**1. Calibration Tracker**
- **Purpose:** Records predicted confidence and actual outcomes
- **Storage:** CMC atoms tagged `confidence_calibration`
- **Schema:** `{task_id, predicted, actual, task_category, timestamp, confidence_type}`
- **Updates:** Real-time updates after each task completion

**2. Bias Calculator**
- **Purpose:** Calculates calibration bias per task category
- **Algorithm:** Mean difference between predicted and actual
- **Output:** Bias per category: `bias_k = mean(predicted_k - actual_k)`
- **Updates:** Recalculated after each batch of outcomes

**3. Calibration Model**
- **Purpose:** Stores calibration parameters per task category
- **Storage:** CMC atoms tagged `calibration_model`
- **Schema:** `{category, bias, accuracy, sample_size, last_updated}`
- **Usage:** Applied to raw confidence before reporting

**4. ECE Calculator**
- **Purpose:** Computes Expected Calibration Error
- **Algorithm:** Binned calibration error calculation
- **Binning:** Optimal bin count: `sqrt(n)` where n = predictions
- **Output:** ECE score and calibration curve

**5. Dashboard Generator**
- **Purpose:** Generates calibration dashboards and reports
- **Visualizations:** Calibration curves, bias plots, ECE trends
- **Alerts:** Triggers when ECE > 0.10 or bias exceeds thresholds
- **Integration:** CAS dashboards, VIF confidence displays

### Data Flow

**Calibration Flow:**
```
Task Start → Record Predicted Confidence → Execute Task → 
Record Actual Outcome → Calculate Error → Update Calibration Model → 
Apply Calibration to Future Predictions
```

**Bias Calculation Flow:**
```
Collect Outcomes → Group by Task Category → Calculate Mean Error → 
Update Bias Model → Store in CMC → Apply to Raw Confidence
```

**ECE Calculation Flow:**
```
Collect Predictions → Bin by Confidence Level → Calculate Observed Rate → 
Compare to Predicted → Compute ECE → Generate Calibration Curve
```

## Operational Guidance

### Calibration Best Practices

**1. Regular Calibration Updates**
- Update calibration models after every 20-50 outcomes
- Recalculate bias per category weekly
- Recompute ECE monthly
- Review calibration curves quarterly

**2. Task Category Management**
- Define clear task categories (documentation, code, organizational)
- Ensure sufficient samples per category (minimum 10 outcomes)
- Merge similar categories if sample size too small
- Split categories if bias varies significantly within category

**3. Confidence Type Selection**
- Use Direction Confidence for strategic decisions
- Use Execution Confidence for technical tasks
- Use Autonomous Confidence for independent work
- Use Collaborative Confidence for team tasks

**4. Calibration Thresholds**
- ECE < 0.05: Well calibrated, continue monitoring
- ECE 0.05-0.10: Acceptable, minor adjustments needed
- ECE > 0.10: Poor calibration, requires recalibration
- Bias > 0.15: Significant bias, immediate correction needed

### Troubleshooting Guide

**Problem: High ECE (> 0.10)**
- **Causes:** Model drift, insufficient data, category mismatch
- **Solutions:** Recalibrate model, increase sample size, refine categories

**Problem: Persistent Overconfidence**
- **Causes:** Optimistic priors, insufficient penalty for failures
- **Solutions:** Adjust priors downward, increase failure weight, tighten gates

**Problem: Persistent Underconfidence**
- **Causes:** Pessimistic priors, excessive penalty for failures
- **Solutions:** Adjust priors upward, decrease failure weight, encourage automation

**Problem: Category-Specific Bias**
- **Causes:** Different difficulty levels, different success criteria
- **Solutions:** Split categories, adjust category-specific priors, refine task classification

## Mathematical Foundations
