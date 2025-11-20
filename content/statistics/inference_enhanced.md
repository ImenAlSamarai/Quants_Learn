---
title: Statistical Inference
category: statistics
subcategory: inference
difficulty: 2
---

# Statistical Inference

Statistical inference involves drawing conclusions about populations based on sample data. It provides methods to estimate parameters, construct confidence intervals, and test hypotheses.

## Sampling Distributions

### Sampling Distribution of the Mean

If X₁, ..., Xₙ are i.i.d. with mean μ and variance σ²:

**Sample mean**:
```
X̄ = (1/n) Σ Xᵢ
```

**Properties**:
```
E[X̄] = μ
Var(X̄) = σ²/n
SE(X̄) = σ/√n    (standard error)
```

### Central Limit Theorem (CLT)

For large n, regardless of original distribution:
```
X̄ ~ N(μ, σ²/n)    approximately

Z = (X̄ - μ)/(σ/√n) ~ N(0, 1)
```

**Practical rule**: n ≥ 30 usually sufficient

**Implications**:
- Can use normal distribution for inference
- Forms basis for confidence intervals and hypothesis tests

## Point Estimation

### Estimator Properties

**Unbiased**: E[θ̂] = θ
**Consistent**: θ̂ → θ as n → ∞
**Efficient**: Minimum variance among unbiased estimators

### Method of Moments

Match sample moments to population moments.

**Example** (Normal distribution):
```
μ̂ = X̄
σ̂² = (1/n) Σ (Xᵢ - X̄)²
```

### Maximum Likelihood Estimation (MLE)

Find parameter values that maximize likelihood:
```
L(θ | x₁, ..., xₙ) = Π f(xᵢ | θ)
```

Maximize log-likelihood:
```
ℓ(θ) = log L(θ) = Σ log f(xᵢ | θ)
```

**Properties**:
- Asymptotically unbiased
- Asymptotically efficient
- Invariant under transformations

**Example** (Normal distribution):
```
μ̂_MLE = X̄
σ̂²_MLE = (1/n) Σ (Xᵢ - X̄)²
```

**Example** (Exponential distribution):
```
λ̂_MLE = 1/X̄
```

## Confidence Intervals

### Confidence Interval for Mean (σ known)

```
X̄ ± z_{α/2} · σ/√n
```

For 95% CI: z_{0.025} = 1.96

### Confidence Interval for Mean (σ unknown)

Use t-distribution with n-1 degrees of freedom:
```
X̄ ± t_{α/2, n-1} · s/√n
```

Where s is sample standard deviation:
```
s = √[(1/(n-1)) Σ (Xᵢ - X̄)²]
```

### Interpretation

"We are 95% confident that the true mean lies in this interval."

**Correct**: In repeated sampling, 95% of intervals contain true parameter.

**Incorrect**: "Probability that μ is in interval is 95%." (Frequentist perspective: μ is fixed)

### Confidence Interval for Proportion

For large n:
```
p̂ ± z_{α/2} √[p̂(1-p̂)/n]
```

### Confidence Interval for Variance

Using chi-square distribution:
```
[(n-1)s²/χ²_{α/2, n-1}, (n-1)s²/χ²_{1-α/2, n-1}]
```

## Hypothesis Testing

### Framework

**Null hypothesis H₀**: Claim to be tested (status quo)
**Alternative hypothesis H₁**: What we want to show

**Example**:
- H₀: μ = 0 (no effect)
- H₁: μ ≠ 0 (there is an effect)

### Types of Tests

**Two-tailed**: H₁: μ ≠ μ₀
**Right-tailed**: H₁: μ > μ₀
**Left-tailed**: H₁: μ < μ₀

### Test Statistic and P-value

**Test statistic**: Measure of evidence against H₀
**P-value**: Probability of observing data as extreme as observed, if H₀ is true

**Decision rule**:
- If p-value < α, reject H₀ (significant)
- If p-value ≥ α, fail to reject H₀ (not significant)

Common significance levels: α = 0.05, 0.01, 0.10

### Type I and Type II Errors

|               | H₀ True       | H₀ False      |
|---------------|---------------|---------------|
| Reject H₀     | Type I (α)    | Correct (1-β) |
| Fail to reject| Correct (1-α) | Type II (β)   |

**Type I error**: Rejecting true H₀ (false positive)
**Type II error**: Failing to reject false H₀ (false negative)

**Power**: 1 - β = P(reject H₀ | H₁ true)

### One-Sample t-test

Test H₀: μ = μ₀

**Test statistic**:
```
t = (X̄ - μ₀) / (s/√n) ~ t_{n-1}
```

**P-value** (two-tailed):
```
p = 2P(T > |t|)    where T ~ t_{n-1}
```

### Two-Sample t-test

Test H₀: μ₁ = μ₂

**Pooled variance** (assuming equal variances):
```
s_p² = [(n₁-1)s₁² + (n₂-1)s₂²] / (n₁ + n₂ - 2)
```

**Test statistic**:
```
t = (X̄₁ - X̄₂) / (s_p√[1/n₁ + 1/n₂])
```

**Welch's t-test** (unequal variances): Use modified degrees of freedom.

### Paired t-test

For paired observations (before/after, matched pairs):

Test H₀: μ_d = 0 where d = X₁ - X₂

```
t = d̄ / (s_d/√n)
```

## Financial Applications

### Testing Trading Strategy

H₀: α = 0 (no excess return)
H₁: α > 0 (positive alpha)

From regression: R_t - R_f = α + β(R_m - R_f) + ε_t

```
t_α = α̂ / SE(α̂)
```

If t_α > critical value, strategy has significant alpha.

### Testing Market Efficiency

H₀: Autocorrelation = 0
H₁: Autocorrelation ≠ 0

If significant autocorrelation, market may not be efficient.

### Estimating Expected Return

95% CI for μ:
```
X̄ ± 1.96 · σ̂/√n
```

**Issue**: High uncertainty for short samples!

### Testing Parameter Stability

Test if β changed after event (structural break):

H₀: β_before = β_after
H₁: β_before ≠ β_after

Use Chow test (F-test).

### Risk Parameter Estimation

**VaR confidence interval**: Bootstrap or delta method

**Sharpe ratio inference**:
```
SE(SR̂) ≈ √[(1 + SR²/2)/n]
```

## Multiple Testing

### Problem

Testing k hypotheses, each at α = 0.05:
```
P(at least one Type I error) = 1 - (1-α)^k
```

For k = 20: P ≈ 0.64!

### Bonferroni Correction

Test each hypothesis at α/k:
```
α_adj = α/k
```

Conservative but simple.

### False Discovery Rate (FDR)

Control proportion of false discoveries among rejections.

**Benjamini-Hochberg procedure**: More powerful than Bonferroni.

## Bootstrap Methods

### Basic Bootstrap

1. Resample data with replacement (n observations)
2. Compute statistic of interest
3. Repeat B times (e.g., B = 10,000)
4. Use bootstrap distribution for inference

### Bootstrap Confidence Interval

**Percentile method**:
```
[θ̂*_{α/2}, θ̂*_{1-α/2}]
```

Where θ̂*_p is the p-th percentile of bootstrap distribution.

### Applications

- Confidence intervals for complex statistics
- Hypothesis testing
- Model validation
- Assessing uncertainty in backtests

## Practice Problems

1. Sample: [12%, 8%, -5%, 15%, 10%]. Construct 95% CI for mean return.

2. Test H₀: μ = 0 vs H₁: μ > 0 with X̄ = 2%, s = 5%, n = 50.

3. Strategy A: Sharpe = 1.2 (n=100). Strategy B: Sharpe = 0.9 (n=80). Test if A is significantly better.

4. If testing 100 independent hypotheses at α = 0.05, how many false positives expected?

5. Two portfolios: Before (μ₁ = 10%, σ₁ = 15%, n₁ = 60), After (μ₂ = 12%, σ₂ = 18%, n₂ = 40). Test if mean changed.

## Next Steps

- **Regression Analysis**: Linear models, diagnostics, interpretation
- **Bayesian Inference**: Prior, likelihood, posterior
- **Time Series**: Autocorrelation, ARMA models, forecasting
- **Nonparametric Methods**: Tests without distributional assumptions
- **Experimental Design**: A/B testing, causal inference


## Heavy-Tailed Distributions and Financial Reality

### Introduction: Beyond the Gaussian Assumption

Classical statistical inference often assumes data follows a Gaussian (normal) distribution. This assumption underlies many standard techniques like t-tests, ANOVA, and confidence intervals based on the Central Limit Theorem. However, **financial data exhibits "fat tails"** - extreme events occur far more frequently than predicted by Gaussian models.

This section introduces heavy-tailed distributions that better describe financial reality, drawing from Bouchaud & Potters' "Theory of Financial Risk."

**Why This Matters:**
- Market crashes (Black Monday 1987, 2008 Financial Crisis) are far more common than Gaussian models predict
- Traditional risk measures (volatility, VaR) can severely underestimate tail risk
- Portfolio optimization and derivatives pricing require accurate tail modeling

---

### Lévy Distributions and Power-Law Tails

**From Bouchaud, Section 1.8:**

Lévy distributions appear naturally when modeling phenomena with multiple scales - from small fluctuations to large jumps. Unlike Gaussian distributions with exponentially decaying tails, Lévy distributions have **power-law (Paretian) tails**:

```
L_μ(x) ~ μA_μ / |x|^(1+μ)    for |x| → ∞
```

where:
- **μ (0 < μ < 2)**: Tail exponent (also called α)
  - μ = 2: Reduces to Gaussian
  - μ < 2: Fat tails (power-law decay)
  - Smaller μ → Fatter tails → More extreme events

- **A_μ**: Tail amplitude (scale parameter)
  - Controls the magnitude of large fluctuations
  - Higher A_μ → More frequent extreme events

**Critical Property: Diverging Moments**

When μ ≤ 2, the **variance is formally infinite**:

```
Var(X) = ∫ x² L_μ(x) dx = ∞    when μ ≤ 2
```

**Implications:**
- Standard deviation doesn't exist mathematically
- Sample variance keeps growing with more data
- Traditional volatility measures are unreliable
- Sharpe ratio and similar metrics break down

When μ ≤ 1, even the **mean is undefined**!

**Characteristic Function:**

Unlike Gaussian distributions, Lévy distributions are more easily described by their characteristic function:

```
ˆL_μ(z) = exp(-a_μ |z|^μ)
```

For μ = 1 (Cauchy distribution), there's an explicit form:

```
L_1(x) = A / (x² + π²A²)
```

**Visual Behavior:**
- Sharp peak around zero
- Fat tails extending far into extremes
- "Missing middle" - intermediate events less likely than Gaussian
- As μ decreases from 2, distribution becomes more peaked and tails get fatter

**Truncated Lévy Distributions:**

In practice, pure power-law tails extend to infinity, which is unrealistic. **Truncated Lévy distributions** add an exponential cut-off for very large values while preserving power-law behavior in intermediate range:

```
ˆL^(t)_μ(z) = exp[-a_μ((α² + z²)^(μ/2) cos(μ arctan(|z|/α)) - α^μ) / cos(πμ/2)]
```

This gives:
- Power-law tails for x ≪ 1/α
- Exponential decay for x ≫ 1/α
- Finite variance: Var(X) = μ(μ-1)a_μ / (|cos(πμ/2)|α^(μ-2))

**Applications:**
- Modeling stock returns (with realistic cut-offs)
- Credit default events
- Insurance claims
- Commodity price jumps

---

### Student's t-Distribution and Other Heavy-Tailed Distributions

**From Bouchaud, Section 1.9:**

While Lévy distributions are theoretically important, the **Student's t-distribution** is often more practical for financial applications due to its simpler parameterization and finite moments.

**Student's t-Distribution:**

With ν degrees of freedom:

```
P_ν(x) = Γ((ν+1)/2) / (√(νπ) Γ(ν/2)) · 1 / (1 + x²/ν)^((ν+1)/2)
```

**Key Properties:**
- **Kurtosis**: κ = 6/(ν - 4)    (for ν > 4)
- ν = ∞: Converges to Gaussian
- Small ν: Fat tails
- ν = 3: Often good fit for daily stock returns
- ν = 5-10: Typical range for financial data

**Moments:**
- Mean exists for ν > 1
- Variance exists for ν > 2
- Higher moments exist for ν > k

**Comparison with Lévy Distributions:**
- Student's t has tail behavior similar to truncated Lévy with μ close to 2
- Easier parameter estimation (Maximum Likelihood works well)
- Finite variance for ν > 2 (unlike pure Lévy)
- Widely supported in statistical software

**When to Use Each Distribution:**

| Distribution | Best For | Advantages | Disadvantages |
|-------------|----------|------------|---------------|
| **Gaussian** | Well-behaved data, large samples | Simple, CLT applies | Underestimates tail risk |
| **Student's t** | Financial returns, moderate tails | Easy to estimate, practical | Less flexible for very fat tails |
| **Lévy (μ < 2)** | Extreme tails, theoretical models | Captures severe tail events | Infinite variance, hard to estimate |
| **Truncated Lévy** | Realistic tail modeling | Flexible, finite variance | Complex parameterization |

**Empirical Detection of Heavy Tails:**

How to identify if your data has fat tails:

1. **Visual Inspection:**
   - Q-Q plot against normal distribution
   - Log-log plot of tail probabilities
   - If tails deviate from straight line → heavy tails

2. **Kurtosis:**
   - Excess kurtosis > 0 indicates fat tails
   - Financial returns typically have κ = 3-10 (vs 0 for Gaussian)

3. **Hill Estimator:**
   - Estimates tail exponent μ from empirical data
   - Based on order statistics of extreme values

4. **Statistical Tests:**
   - Kolmogorov-Smirnov test
   - Anderson-Darling test (more sensitive to tails)
   - Jarque-Bera test (tests normality via skewness/kurtosis)

**Practical Workflow:**

```
1. Plot data distribution → Check for fat tails visually
2. Calculate excess kurtosis → Quantify tail heaviness
3. Fit Student's t → Easy first attempt
4. Estimate tail exponent → Use Hill estimator
5. Compare models → AIC/BIC for Gaussian vs t vs Lévy
6. Validate → Backtest risk measures on out-of-sample data
```

---

### Implications for Statistical Inference

The presence of heavy tails fundamentally changes how we do inference:

**Confidence Intervals:**
- With infinite variance, standard error √(σ²/n) is meaningless
- Need robust methods: bootstrap, quantile-based intervals
- Intervals will be wider than Gaussian-based estimates

**Hypothesis Testing:**
- t-tests assume normality (or CLT convergence)
- With heavy tails, convergence to normality is slow
- Alternative: permutation tests, robust tests

**Parameter Estimation:**
- MLE still works but may be unstable with fat tails
- Robust estimators: trimmed mean, median, MAD
- Bayesian methods with informative priors can help

**Sample Size Requirements:**
- CLT requires much larger n with heavy tails
- Rule of thumb: n ≥ 100 for mild fat tails (μ ≈ 1.7)
- May need n > 1000 for severe tails (μ < 1.5)

**Risk Measurement:**
- VaR underestimates risk with fat tails
- Expected Shortfall (CVaR) more appropriate
- Drawdown-based measures more robust

---

### Further Reading

**Key References:**
- Bouchaud, J.-P., & Potters, M. (2003). *Theory of Financial Risk and Derivative Pricing*
- Mandelbrot, B. (1963). "The Variation of Certain Speculative Prices"
- Fama, E. (1965). "The Behavior of Stock-Market Prices"
- Cont, R. (2001). "Empirical Properties of Asset Returns: Stylized Facts and Statistical Issues"

**Related Topics:**
- Extreme Value Theory (see separate topic)
- Expected Shortfall and Tail Risk Measures
- GARCH Models (heavy tails in conditional distributions)
- Stable Distributions and Generalized CLT

---

## Practice Problems

1. **Tail Behavior**: A distribution has power-law tail with μ = 1.5. Does the variance exist? Does the mean exist?

2. **Kurtosis Calculation**: Student's t with ν = 6 degrees of freedom. Calculate excess kurtosis.

3. **Probability Comparison**: For a Lévy distribution with μ = 1.7 and A_μ = 1, calculate P(X > 10). Compare with Gaussian having same median.

4. **Real Data**: Daily S&P 500 returns show excess kurtosis of 5. Would you model with Gaussian, Student's t, or Lévy? Justify.

5. **Risk Implications**: Portfolio VaR is $1M at 95% confidence under Gaussian. If returns follow Student's t with ν = 4, would true VaR be higher or lower? Why?

---

