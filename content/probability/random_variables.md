---
title: Random Variables and Distributions
category: probability
subcategory: random_variables
difficulty: 2
---

# Random Variables and Distributions

Random variables map outcomes of random experiments to numbers, allowing us to work with probability using mathematical functions and perform calculations essential for finance and statistics.

## Random Variables

### Definition

A random variable X is a function mapping from the sample space to real numbers:
```
X: Ω → ℝ
```

**Example**: For a coin flip (Ω = {H, T}):
```
X(H) = 1
X(T) = 0
```

### Types of Random Variables

**Discrete**: Takes countable values (integers, finite set)
- Examples: Number of defaults, coin flips, Poisson events

**Continuous**: Takes uncountable values (any real number in an interval)
- Examples: Stock returns, interest rates, time

## Discrete Distributions

### Probability Mass Function (PMF)

For discrete X:
```
p(x) = P(X = x)
```

Properties:
- p(x) ≥ 0 for all x
- Σ p(x) = 1

### Cumulative Distribution Function (CDF)

```
F(x) = P(X ≤ x) = Σ_{k≤x} p(k)
```

### Common Discrete Distributions

**Bernoulli(p)**: Single trial with success probability p
```
X ∈ {0, 1}
P(X = 1) = p
P(X = 0) = 1 - p
E[X] = p
Var(X) = p(1-p)
```

**Binomial(n, p)**: Number of successes in n independent trials
```
X ∈ {0, 1, 2, ..., n}
P(X = k) = C(n,k) p^k (1-p)^(n-k)
E[X] = np
Var(X) = np(1-p)
```

**Poisson(λ)**: Number of events in fixed interval
```
X ∈ {0, 1, 2, ...}
P(X = k) = (e^(-λ) λ^k) / k!
E[X] = λ
Var(X) = λ
```

Applications: Trading volume, number of defaults, order arrivals

**Geometric(p)**: Number of trials until first success
```
X ∈ {1, 2, 3, ...}
P(X = k) = (1-p)^(k-1) p
E[X] = 1/p
```

## Continuous Distributions

### Probability Density Function (PDF)

For continuous X:
```
f(x) ≥ 0
∫_{-∞}^{∞} f(x) dx = 1
P(a ≤ X ≤ b) = ∫_a^b f(x) dx
```

**Note**: P(X = x) = 0 for any specific x

### Cumulative Distribution Function (CDF)

```
F(x) = P(X ≤ x) = ∫_{-∞}^x f(t) dt
f(x) = F'(x)
```

### Common Continuous Distributions

**Uniform(a, b)**: Equal probability over [a, b]
```
f(x) = 1/(b-a)    for x ∈ [a, b]
E[X] = (a+b)/2
Var(X) = (b-a)²/12
```

**Exponential(λ)**: Time between Poisson events
```
f(x) = λe^(-λx)    for x ≥ 0
F(x) = 1 - e^(-λx)
E[X] = 1/λ
Var(X) = 1/λ²
```

**Memoryless property**: P(X > s+t | X > s) = P(X > t)

**Normal (Gaussian) N(μ, σ²)**:

Most important distribution in statistics:
```
f(x) = (1/√(2πσ²)) exp(-(x-μ)²/(2σ²))
E[X] = μ
Var(X) = σ²
```

**Standard Normal**: N(0, 1), denoted Z

**Properties**:
- Symmetric around μ
- 68% within μ ± σ
- 95% within μ ± 2σ
- 99.7% within μ ± 3σ

**Standardization**:
```
Z = (X - μ)/σ ~ N(0, 1)
```

**Log-Normal**: If log(X) ~ N(μ, σ²), then X is log-normal
```
f(x) = (1/(xσ√(2π))) exp(-(ln x - μ)²/(2σ²))    for x > 0
E[X] = e^(μ + σ²/2)
Var(X) = e^(2μ + σ²)(e^(σ²) - 1)
```

Used for stock prices (always positive, skewed right).

**Student's t-distribution**: Heavy-tailed alternative to normal
```
Degrees of freedom: ν
As ν → ∞, converges to normal
```

Used when estimating parameters with small samples.

## Transformations of Random Variables

### Linear Transformation

If Y = aX + b:
```
E[Y] = aE[X] + b
Var(Y) = a²Var(X)
```

### General Transformation

If Y = g(X) and g is monotonic:
```
f_Y(y) = f_X(g^{-1}(y)) |d/dy g^{-1}(y)|
```

## Joint Distributions

### Joint PMF (Discrete)

```
p(x, y) = P(X = x, Y = y)
```

### Joint PDF (Continuous)

```
∫∫ f(x, y) dx dy = 1
P((X,Y) ∈ A) = ∫∫_A f(x, y) dx dy
```

### Marginal Distributions

```
f_X(x) = ∫ f(x, y) dy
f_Y(y) = ∫ f(x, y) dx
```

### Independence

X and Y are independent if:
```
f(x, y) = f_X(x) · f_Y(y)
```

### Covariance

```
Cov(X, Y) = E[(X - μ_X)(Y - μ_Y)] = E[XY] - E[X]E[Y]
```

If independent, then Cov(X, Y) = 0 (converse not always true).

### Correlation

```
ρ(X, Y) = Cov(X, Y) / (σ_X σ_Y) ∈ [-1, 1]
```

## Financial Applications

### Stock Returns

Often modeled as normal:
```
R ~ N(μ, σ²)
```

### Stock Prices

Log-normal model:
```
S_T = S_0 e^((μ - σ²/2)T + σ√T Z)
```

Where Z ~ N(0, 1).

### Portfolio Returns

If X₁, ..., Xₙ are returns with weights w₁, ..., wₙ:
```
R_p = Σ wᵢXᵢ
E[R_p] = Σ wᵢE[Xᵢ]
Var(R_p) = Σᵢ Σⱼ wᵢwⱼCov(Xᵢ, Xⱼ)
```

### Value at Risk (VaR)

For normal returns:
```
VaR_α = μ - z_α σ
```

Where z_α is the α-quantile of standard normal.

## Practice Problems

1. X ~ Binomial(10, 0.3). Find P(X = 3) and E[X].

2. Returns ~ N(0.08, 0.04). What's probability of negative return?

3. If X ~ Uniform(0, 1), find PDF of Y = -2ln(X).

4. Two assets with σ₁ = 0.2, σ₂ = 0.3, ρ = 0.4. Portfolio: 60% asset 1, 40% asset 2. Find portfolio variance.

## Next Steps

- **Expectation and Moments**: Computing averages and spread
- **Limit Theorems**: Convergence properties
- **Stochastic Processes**: Time-dependent random variables
- **Multivariate Distributions**: Normal, copulas, dependence
