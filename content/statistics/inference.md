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
