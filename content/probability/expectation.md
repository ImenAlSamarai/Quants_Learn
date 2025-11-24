---
title: Expectation and Moments
category: probability
subcategory: expectation
difficulty: 2
---

# Expectation and Moments

Expectation provides the average or expected value of a random variable, forming the foundation for decision-making under uncertainty. Moments characterize the shape and properties of distributions.

## Expected Value (Mean)

### Definition

**Discrete**:
```
E[X] = Σ x·P(X = x)
```

**Continuous**:
```
E[X] = ∫_{-∞}^{∞} x·f(x) dx
```

**Interpretation**: Long-run average if experiment repeated many times.

### Properties of Expectation

1. **Linearity**: E[aX + bY + c] = aE[X] + bE[Y] + c
2. **Constant**: E[c] = c
3. **Independence**: If X ⊥ Y, then E[XY] = E[X]·E[Y]

**Note**: Linearity holds even for dependent variables!

### Law of the Unconscious Statistician (LOTUS)

To find E[g(X)], don't need distribution of g(X):

**Discrete**: E[g(X)] = Σ g(x)·P(X = x)
**Continuous**: E[g(X)] = ∫ g(x)·f(x) dx

## Variance and Standard Deviation

### Variance

Measures spread around the mean:
```
Var(X) = E[(X - μ)²] = E[X²] - (E[X])²
```

**Standard deviation**: σ = √Var(X)

### Properties of Variance

1. Var(aX + b) = a²Var(X)
2. If X ⊥ Y: Var(X + Y) = Var(X) + Var(Y)
3. General: Var(X + Y) = Var(X) + Var(Y) + 2Cov(X, Y)

## Higher Moments

### Moment Definitions

**nth raw moment**:
```
E[X^n]
```

**nth central moment**:
```
E[(X - μ)^n]
```

### Skewness (3rd moment)

Measures asymmetry:
```
γ₁ = E[(X - μ)³] / σ³
```

- γ₁ > 0: Right-skewed (long right tail)
- γ₁ < 0: Left-skewed (long left tail)
- γ₁ = 0: Symmetric (e.g., normal distribution)

### Kurtosis (4th moment)

Measures tail heaviness:
```
γ₂ = E[(X - μ)⁴] / σ⁴ - 3
```

- γ₂ > 0: Heavy tails (leptokurtic)
- γ₂ < 0: Light tails (platykurtic)
- γ₂ = 0: Normal tails (mesokurtic)

**Excess kurtosis**: Subtract 3 so normal has kurtosis 0.

## Moment Generating Function (MGF)

### Definition

```
M_X(t) = E[e^{tX}]
```

### Properties

1. **Moments**: E[X^n] = M_X^{(n)}(0)
2. **Uniqueness**: MGF determines distribution uniquely
3. **Independence**: If X ⊥ Y, then M_{X+Y}(t) = M_X(t)·M_Y(t)

### Common MGFs

**Normal N(μ, σ²)**:
```
M_X(t) = exp(μt + σ²t²/2)
```

**Exponential(λ)**:
```
M_X(t) = λ/(λ - t)    for t < λ
```

**Poisson(λ)**:
```
M_X(t) = exp(λ(e^t - 1))
```

## Conditional Expectation

### Definition

```
E[X|Y = y] = Σ x·P(X = x|Y = y)    (discrete)
E[X|Y = y] = ∫ x·f(x|y) dx         (continuous)
```

### Law of Iterated Expectations

```
E[X] = E[E[X|Y]]
```

**Application**: Decomposing complex expectations.

### Conditional Variance

```
Var(X) = E[Var(X|Y)] + Var(E[X|Y])
```

## Covariance and Correlation

### Covariance

```
Cov(X, Y) = E[(X - μ_X)(Y - μ_Y)]
           = E[XY] - E[X]E[Y]
```

**Properties**:
- Cov(X, X) = Var(X)
- Cov(X, Y) = Cov(Y, X)
- Cov(aX + b, cY + d) = ac·Cov(X, Y)

### Correlation

```
ρ(X, Y) = Cov(X, Y) / (σ_X σ_Y) ∈ [-1, 1]
```

**Interpretation**:
- ρ = 1: Perfect positive linear relationship
- ρ = -1: Perfect negative linear relationship
- ρ = 0: No linear relationship (but may have nonlinear!)

### Properties

1. -1 ≤ ρ ≤ 1
2. |ρ| = 1 iff Y = aX + b for some a, b
3. If X ⊥ Y, then ρ = 0 (converse not always true)

## Inequalities

### Markov's Inequality

For non-negative X and a > 0:
```
P(X ≥ a) ≤ E[X]/a
```

### Chebyshev's Inequality

For any k > 0:
```
P(|X - μ| ≥ kσ) ≤ 1/k²
```

**Example**: At least 75% of data within 2σ of mean.

### Jensen's Inequality

For convex function φ:
```
E[φ(X)] ≥ φ(E[X])
```

For concave function φ:
```
E[φ(X)] ≤ φ(E[X])
```

## Financial Applications

### Expected Return

```
E[R] = Σ r_i · p_i
```

Or for continuous:
```
E[R] = ∫ r · f(r) dr
```

### Portfolio Expected Return

```
E[R_p] = Σ w_i E[R_i]
```

### Portfolio Variance

```
Var(R_p) = Σᵢ Σⱼ w_i w_j Cov(R_i, R_j)
         = w'Σw
```

Where Σ is the covariance matrix.

### Sharpe Ratio

```
SR = (E[R] - R_f) / σ_R
```

Higher is better (more return per unit risk).

### Expected Utility

Instead of maximizing E[X], maximize E[u(X)]:
```
max E[u(W)]
```

Where u is utility function (e.g., logarithmic, exponential).

### Risk-Neutral Pricing

Option value is discounted expected payoff under risk-neutral measure:
```
V = e^{-rT} E^Q[payoff(S_T)]
```

### Greeks as Expectations

**Delta**: E[∂payoff/∂S]
**Vega**: E[∂payoff/∂σ]

Using Monte Carlo simulation.

## Useful Formulas

### Sum of Independent Variables

If X₁, ..., Xₙ are independent:
```
E[Σ Xᵢ] = Σ E[Xᵢ]
Var(Σ Xᵢ) = Σ Var(Xᵢ)
```

### Product of Independent Variables

If X ⊥ Y:
```
E[XY] = E[X]·E[Y]
Var(XY) = E[X²]E[Y²] - (E[X])²(E[Y])²
```

## Practice Problems

1. X ~ Binomial(n, p). Find E[X] and Var(X) using definitions.

2. Returns: 10%, 5%, -3%, 8% with equal probability. Find E[R] and σ_R.

3. Portfolio: 50% stock A (μ=12%, σ=20%), 50% stock B (μ=8%, σ=15%), ρ=0.3. Find E[R_p] and σ_p.

4. Use Chebyshev: If μ=10, σ=2, bound P(6 < X < 14).

5. Show that Var(X) = E[X²] - (E[X])².

## Next Steps

- **Limit Theorems**: Law of Large Numbers, Central Limit Theorem
- **Stochastic Processes**: Time series of random variables
- **Statistical Inference**: Using samples to estimate expectations
- **Risk Measures**: VaR, CVaR, and coherent risk measures
