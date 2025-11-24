---
title: Probability Theory
category: probability
difficulty: 2
---

# Probability Theory

Probability is the mathematical framework for quantifying uncertainty, forming the foundation of statistical inference, risk management, and quantitative finance. It provides the tools to model randomness and make informed decisions under uncertainty.

## Why Probability Matters in Quant Finance

- **Risk Modeling**: Quantifying the likelihood and magnitude of losses
- **Options Pricing**: Modeling future asset price distributions
- **Portfolio Theory**: Balancing expected returns against uncertainty
- **Stochastic Processes**: Modeling price movements over time
- **Bayesian Inference**: Updating beliefs based on new information

## Fundamental Concepts

1. **Sample Spaces and Events**: Defining possible outcomes
2. **Probability Axioms**: Kolmogorov's axioms provide rigorous foundation
3. **Conditional Probability**: Updating probabilities given new information
4. **Random Variables**: Functions mapping outcomes to numbers
5. **Distributions**: Describing probability across possible values
6. **Expectation**: Average or expected value
7. **Limit Theorems**: Law of Large Numbers, Central Limit Theorem

## Key Probability Distributions

### Discrete Distributions
- **Bernoulli**: Single binary outcome (coin flip)
- **Binomial**: Number of successes in n trials
- **Poisson**: Number of events in fixed time interval
- **Geometric**: Number of trials until first success

### Continuous Distributions
- **Uniform**: Equal probability over an interval
- **Normal (Gaussian)**: Bell curve, ubiquitous in nature
- **Exponential**: Time between events in Poisson process
- **Log-normal**: Used for asset prices (always positive)
- **Student's t**: Heavy-tailed alternative to normal

## Applications in Finance

### Value at Risk (VaR)

Quantifying maximum expected loss at a confidence level:
```
P(Loss ≤ VaR_α) = α
```

### Expected Shortfall (CVaR)

Average loss beyond VaR:
```
ES_α = E[Loss | Loss > VaR_α]
```

### Sharpe Ratio

Risk-adjusted return:
```
SR = (E[R] - R_f) / σ_R
```

### Black-Scholes Model

Assumes log-normal distribution of stock prices:
```
S_T = S_0 · e^((μ - σ²/2)T + σ√T·Z)    where Z ~ N(0,1)
```

### Monte Carlo Simulation

Estimating option prices by simulating price paths:
```
V ≈ e^(-rT) · (1/N) Σ payoff(S_T^(i))
```

## Stochastic Processes

### Random Walk

```
S_t = S_(t-1) + ε_t    where ε_t ~ N(0, σ²)
```

### Brownian Motion (Wiener Process)

Continuous-time random walk with properties:
- W_0 = 0
- Independent increments
- W_t ~ N(0, t)
- Continuous paths

### Geometric Brownian Motion

Model for stock prices:
```
dS_t = μS_t dt + σS_t dW_t
```

## Conditional Probability and Bayes' Theorem

### Bayes' Theorem

```
P(A|B) = P(B|A)·P(A) / P(B)
```

Applications:
- Updating market predictions with new data
- Spam filtering
- Credit risk assessment
- Fraud detection

## Moment Generating Functions

Used to characterize distributions and compute moments:
```
M_X(t) = E[e^(tX)]
E[X^n] = M_X^(n)(0)
```

## Independence and Correlation

### Independence

X and Y are independent if:
```
P(X ∈ A, Y ∈ B) = P(X ∈ A)·P(Y ∈ B)
```

### Covariance and Correlation

```
Cov(X, Y) = E[(X - E[X])(Y - E[Y])]
Corr(X, Y) = Cov(X, Y) / (σ_X · σ_Y)
```

## Next Topics

Build on probability foundations with:
- **Statistics**: Inference, hypothesis testing, regression
- **Stochastic Calculus**: Ito's lemma, Black-Scholes derivation
- **Time Series**: ARMA, GARCH, forecasting
- **Machine Learning**: Bayesian methods, probabilistic models
