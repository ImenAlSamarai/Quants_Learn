---
title: Statistics
category: statistics
difficulty: 2
---

# Statistics

Statistics is the science of collecting, analyzing, and interpreting data to make informed decisions under uncertainty. It provides the tools to draw conclusions from samples, test hypotheses, and build predictive models.

## Why Statistics Matters in Quant Finance

- **Backtesting**: Evaluating trading strategy performance on historical data
- **Parameter Estimation**: Fitting models to market data
- **Hypothesis Testing**: Testing market efficiency, anomalies, and strategies
- **Regression Analysis**: Modeling relationships between variables
- **Time Series**: Forecasting returns, volatility, and risk
- **Risk Management**: Estimating VaR, stress testing, and scenario analysis

## Core Statistical Concepts

1. **Descriptive Statistics**: Summarizing data with measures of center and spread
2. **Statistical Inference**: Drawing conclusions about populations from samples
3. **Hypothesis Testing**: Testing claims about parameters
4. **Confidence Intervals**: Quantifying uncertainty in estimates
5. **Regression**: Modeling relationships between variables
6. **Time Series Analysis**: Analyzing sequential data over time

## Key Areas

### Descriptive Statistics

**Measures of Center**:
- Mean (average)
- Median (middle value)
- Mode (most frequent)

**Measures of Spread**:
- Variance and standard deviation
- Range and interquartile range
- Mean absolute deviation

**Measures of Shape**:
- Skewness (asymmetry)
- Kurtosis (tail heaviness)

### Inferential Statistics

**Point Estimation**: Estimating population parameters
- Method of moments
- Maximum likelihood estimation (MLE)
- Bayesian estimation

**Interval Estimation**: Constructing confidence intervals
- Confidence intervals for means
- Confidence intervals for proportions
- Bootstrap confidence intervals

**Hypothesis Testing**: Testing statistical claims
- Null and alternative hypotheses
- Type I and Type II errors
- p-values and significance levels
- t-tests, chi-square tests, ANOVA

### Regression Analysis

**Linear Regression**: Modeling linear relationships
```
Y = β₀ + β₁X + ε
```

**Multiple Regression**: Multiple predictors
```
Y = β₀ + β₁X₁ + β₂X₂ + ... + βₚXₚ + ε
```

**Applications**:
- Capital Asset Pricing Model (CAPM)
- Fama-French factor models
- Predicting returns from factors

### Time Series Analysis

**Components**:
- Trend: Long-term direction
- Seasonality: Periodic patterns
- Cyclical: Non-periodic oscillations
- Irregular: Random noise

**Models**:
- Autoregressive (AR)
- Moving Average (MA)
- ARMA and ARIMA
- GARCH (volatility modeling)

## Financial Applications

### Return Analysis

**Sample statistics**:
```
μ̂ = (1/n) Σ rᵢ
σ̂² = (1/(n-1)) Σ (rᵢ - μ̂)²
```

**Sharpe Ratio**:
```
SR = (μ̂ - r_f) / σ̂
```

### Hypothesis Testing

**Testing market efficiency**:
- H₀: Returns are unpredictable (random walk)
- H₁: Returns are predictable

**Testing trading strategies**:
- H₀: Strategy has no excess returns
- H₁: Strategy has positive alpha

### Regression Models

**CAPM**:
```
E[R_i] - R_f = β_i(E[R_m] - R_f)
```

Estimate β via regression:
```
R_i - R_f = α + β(R_m - R_f) + ε
```

**Fama-French 3-Factor**:
```
R_i - R_f = α + β₁(R_m - R_f) + β₂SMB + β₃HML + ε
```

### Volatility Estimation

**Historical volatility**:
```
σ̂ = √[(252/n) Σ r²ᵢ]    (annualized)
```

**GARCH(1,1)**:
```
σ²ₜ = ω + α·ε²ₜ₋₁ + β·σ²ₜ₋₁
```

### Value at Risk (VaR)

**Parametric VaR** (assuming normality):
```
VaR_α = μ - z_α·σ
```

**Historical VaR**: Use empirical quantiles

**Monte Carlo VaR**: Simulate future scenarios

### Backtesting

**Sharpe Ratio significance**:
```
t = SR·√n / √(1 + SR²/2)
```

**Multiple testing correction**: Bonferroni, FDR

## Common Statistical Tests

### t-test

Test if mean differs from hypothesized value:
```
t = (x̄ - μ₀) / (s/√n)
```

### Chi-Square Test

Test independence or goodness-of-fit:
```
χ² = Σ (O_i - E_i)² / E_i
```

### F-test

Compare variances or test regression significance:
```
F = s₁²/s₂²
```

### Correlation Test

Test if correlation is significant:
```
t = r√(n-2) / √(1-r²)
```

## Bootstrap and Resampling

**Bootstrap**: Resample data with replacement to estimate sampling distribution

**Applications**:
- Confidence intervals for complex statistics
- Model validation
- Robustness checks

## Machine Learning Connection

**Statistical Learning**: Intersection of statistics and ML
- Bias-variance tradeoff
- Cross-validation
- Regularization (Ridge, Lasso)
- Feature selection

## Practice Problems

1. Returns: [5%, -2%, 8%, 3%, -1%]. Calculate mean, variance, and Sharpe ratio (assume r_f = 2%).

2. Test H₀: μ = 0 vs H₁: μ ≠ 0 with sample mean 0.5%, std 2%, n = 100.

3. Regress stock returns on market returns. Interpret β coefficient.

4. Calculate 95% VaR assuming returns ~ N(8%, 20%) for $1M portfolio.

## Next Steps

- **Advanced Regression**: Ridge, Lasso, nonlinear models
- **Bayesian Statistics**: Prior distributions, posterior inference
- **Survival Analysis**: Time-to-event modeling
- **Multivariate Statistics**: PCA, factor analysis, clustering
- **Experimental Design**: A/B testing, causal inference
