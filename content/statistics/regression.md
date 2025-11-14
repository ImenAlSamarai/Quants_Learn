---
title: Regression Analysis
category: statistics
subcategory: regression
difficulty: 3
---

# Regression Analysis

Regression analysis models the relationship between a dependent variable and one or more independent variables, enabling prediction, understanding relationships, and testing theories in finance.

## Simple Linear Regression

### Model

```
Y = β₀ + β₁X + ε
```

Where:
- Y: Dependent variable (response)
- X: Independent variable (predictor)
- β₀: Intercept
- β₁: Slope
- ε: Error term, ε ~ N(0, σ²)

**Interpretation**: One unit increase in X leads to β₁ unit change in Y.

### Ordinary Least Squares (OLS)

Minimize sum of squared residuals:
```
min Σ (yᵢ - β₀ - β₁xᵢ)²
```

**Solutions**:
```
β̂₁ = Cov(X, Y) / Var(X) = Σ(xᵢ - x̄)(yᵢ - ȳ) / Σ(xᵢ - x̄)²
β̂₀ = ȳ - β̂₁x̄
```

### R-squared (Coefficient of Determination)

```
R² = 1 - SSR/SST = SSE/SST
```

Where:
- SST = Σ(yᵢ - ȳ)²: Total sum of squares
- SSR = Σ(yᵢ - ŷᵢ)²: Residual sum of squares
- SSE = Σ(ŷᵢ - ȳ)²: Explained sum of squares

**Interpretation**: R² = 0.75 means 75% of variance in Y is explained by X.

Range: 0 ≤ R² ≤ 1 (higher is better)

### Inference on Coefficients

**Standard errors**:
```
SE(β̂₁) = σ̂ / √[Σ(xᵢ - x̄)²]
SE(β̂₀) = σ̂ √[1/n + x̄²/Σ(xᵢ - x̄)²]
```

Where σ̂² = SSR/(n-2) is residual variance estimate.

**t-test for β₁**:
```
H₀: β₁ = 0
t = β̂₁ / SE(β̂₁) ~ t_{n-2}
```

**Confidence interval**:
```
β̂₁ ± t_{α/2, n-2} · SE(β̂₁)
```

## Multiple Linear Regression

### Model

```
Y = β₀ + β₁X₁ + β₂X₂ + ... + βₚXₚ + ε
```

**Matrix form**:
```
Y = Xβ + ε
```

### OLS Estimator

```
β̂ = (X'X)⁻¹X'Y
```

**Properties** (under standard assumptions):
- Unbiased: E[β̂] = β
- Minimum variance among linear unbiased estimators (BLUE)
- Normally distributed (if ε ~ N)

### Adjusted R-squared

Penalizes adding predictors:
```
R̄² = 1 - (1 - R²)(n - 1)/(n - p - 1)
```

Always use R̄² when comparing models with different numbers of predictors.

### F-test for Overall Significance

Test H₀: β₁ = β₂ = ... = βₚ = 0

```
F = [SSE/p] / [SSR/(n-p-1)] ~ F_{p, n-p-1}
```

If F > critical value, at least one predictor is significant.

### t-test for Individual Coefficients

Test H₀: βⱼ = 0

```
t = β̂ⱼ / SE(β̂ⱼ) ~ t_{n-p-1}
```

## Model Assumptions

1. **Linearity**: Relationship is linear
2. **Independence**: Observations are independent
3. **Homoscedasticity**: Constant error variance
4. **Normality**: Errors are normally distributed
5. **No multicollinearity**: Predictors not highly correlated

## Diagnostics

### Residual Analysis

Plot residuals vs fitted values:
- Random scatter → assumptions satisfied
- Pattern → assumption violated

**Standardized residuals**:
```
rᵢ = eᵢ / (σ̂√(1 - hᵢᵢ))
```

Where hᵢᵢ is leverage (diagonal of hat matrix).

### Checking Normality

Q-Q plot: Plot quantiles of residuals vs theoretical normal quantiles.

Shapiro-Wilk test for normality.

### Checking Homoscedasticity

Plot |residuals| or residuals² vs fitted values.

Breusch-Pagan test.

### Multicollinearity

**Variance Inflation Factor (VIF)**:
```
VIF_j = 1 / (1 - R²_j)
```

Where R²_j is from regressing Xⱼ on other predictors.

**Rule of thumb**: VIF > 10 indicates problematic multicollinearity.

### Influential Observations

**Cook's Distance**: Measures influence of each observation.

```
D_i = (1/(p+1)) · (rᵢ² / (1 - hᵢᵢ)) · hᵢᵢ
```

**Rule**: D_i > 1 is concerning.

## Financial Applications

### Capital Asset Pricing Model (CAPM)

```
R_i - R_f = α + β(R_m - R_f) + ε
```

**Interpretation**:
- β: Systematic risk (market sensitivity)
- α (Jensen's alpha): Excess return (skill)

**Estimates**:
- β̂ > 1: More volatile than market
- β̂ < 1: Less volatile than market
- α̂ > 0: Outperforming (if statistically significant)

### Fama-French Three-Factor Model

```
R_i - R_f = α + β₁(R_m - R_f) + β₂SMB + β₃HML + ε
```

Where:
- SMB: Small Minus Big (size factor)
- HML: High Minus Low (value factor)

### Market Model

```
R_i = α + βR_m + ε
```

Estimate β for portfolio construction.

### Pairs Trading

Find cointegrated pairs:
```
Y_t = α + βX_t + ε_t
```

Trade spread: S_t = Y_t - βX_t

### Factor Models

Identify systematic risk factors:
```
R_i = Σ βᵢⱼFⱼ + εᵢ
```

Use PCA or economic theory to select factors.

## Advanced Topics

### Polynomial Regression

```
Y = β₀ + β₁X + β₂X² + ... + βₚX^p + ε
```

Captures nonlinear relationships.

### Interaction Terms

```
Y = β₀ + β₁X₁ + β₂X₂ + β₃(X₁·X₂) + ε
```

Effect of X₁ depends on X₂.

### Dummy Variables

For categorical predictors:
```
Y = β₀ + β₁X + β₂D + ε
```

Where D = 1 for category A, D = 0 for category B.

**Interpretation**: β₂ is the difference in intercepts.

### Logistic Regression

For binary outcomes (Y ∈ {0, 1}):
```
log[P(Y=1)/(1-P(Y=1))] = β₀ + β₁X
```

**Odds ratio**: e^β₁

Applications: Default prediction, classification.

### Regularization

**Ridge regression**: Add penalty λΣβⱼ²
**Lasso regression**: Add penalty λΣ|βⱼ|

Reduces overfitting and performs feature selection (Lasso).

### Time Series Regression

Account for autocorrelation:
- Newey-West standard errors
- ARMA errors
- Generalized Least Squares (GLS)

## Model Selection

### Information Criteria

**Akaike Information Criterion (AIC)**:
```
AIC = 2p - 2log(L)
```

**Bayesian Information Criterion (BIC)**:
```
BIC = p·log(n) - 2log(L)
```

Lower is better. BIC penalizes complexity more.

### Cross-Validation

Split data into training and validation sets.

**k-fold CV**: Divide data into k parts, train on k-1, validate on 1.

Prevents overfitting.

### Stepwise Selection

- **Forward**: Start with no predictors, add one at a time
- **Backward**: Start with all predictors, remove one at a time
- **Stepwise**: Combination of forward and backward

**Warning**: Can lead to overfitting and inflated significance.

## Practice Problems

1. Regress stock returns on market returns. Estimate β and test if significantly different from 1.

2. Data: Y = [10, 12, 15, 18, 20], X = [1, 2, 3, 4, 5]. Find β̂₀, β̂₁, R².

3. Multiple regression with p=5 predictors, n=50, R²=0.6. Test overall significance.

4. VIF values: [1.2, 8.5, 12.3]. Interpret multicollinearity.

5. Regress portfolio returns on Fama-French factors. Interpret coefficients.

## Next Steps

- **Time Series Regression**: Autocorrelation, ARMA errors
- **Panel Data**: Fixed effects, random effects
- **Nonlinear Regression**: Neural networks, tree-based models
- **Quantile Regression**: Beyond mean regression
- **Causal Inference**: Instrumental variables, diff-in-diff
