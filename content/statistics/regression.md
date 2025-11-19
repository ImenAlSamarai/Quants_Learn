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

### Ridge Regression (L2 Regularization)

Ridge regression addresses multicollinearity and overfitting by adding an L2 penalty to the OLS objective function.

#### Objective Function

```
min ||Y - Xβ||² + λ||β||²
```

Where:
- λ ≥ 0: Regularization parameter (tuning parameter)
- ||β||² = Σβⱼ²: L2 norm of coefficients (excludes intercept)

#### Solution

```
β̂_ridge = (X'X + λI)⁻¹X'Y
```

**Key properties**:
- Always invertible even if X'X is singular
- Shrinks coefficients toward zero (but never exactly zero)
- Biased estimator, but can have lower MSE than OLS

#### Bias-Variance Tradeoff

```
MSE(β̂_ridge) = Bias²(β̂_ridge) + Var(β̂_ridge)
```

As λ increases:
- **Bias** increases: Coefficients shrink away from true values
- **Variance** decreases: Estimates more stable
- **MSE** first decreases, then increases (U-shaped curve)

**Optimal λ**: Balances bias and variance to minimize prediction error.

#### Choosing λ (Regularization Parameter)

**Cross-Validation**: Most common approach
```
1. Split data into k folds
2. For each λ in grid:
   - Train on k-1 folds
   - Validate on remaining fold
   - Compute CV error
3. Select λ with minimum CV error
```

**Rule of thumb**: Try logarithmic grid: λ ∈ [10⁻⁵, 10⁻⁴, ..., 10²]

**Analytical approaches**:
- **Generalized Cross-Validation (GCV)**: Approximation to leave-one-out CV
- **AIC/BIC**: Information criteria adapted for regularization

#### Standardization

**Critical**: Always standardize predictors before Ridge regression.

```
X_scaled = (X - μ) / σ
```

**Reason**: Ridge penalty depends on coefficient magnitude, which depends on predictor scale.

**Note**: Intercept β₀ is not penalized (or center Y first).

#### Degrees of Freedom

```
df(λ) = tr[X(X'X + λI)⁻¹X']
```

Effective degrees of freedom decreases as λ increases.

- λ = 0: df = p (OLS)
- λ → ∞: df → 0

#### Ridge Trace

Plot β̂ⱼ(λ) vs λ for each predictor j.

**Interpretation**:
- Shows how coefficients shrink as λ increases
- Coefficients of collinear predictors stabilize with regularization
- Helps identify important predictors (last to shrink)

#### Ridge vs OLS

| Aspect | OLS | Ridge |
|--------|-----|-------|
| Multicollinearity | Unstable, high variance | Stable estimates |
| Overfitting | Prone when p large | Reduced |
| Invertibility | Requires X'X invertible | Always works |
| Interpretability | Clear | Biased coefficients |
| Variance | High (p ≈ n) | Lower |
| Bias | Unbiased | Biased |

**When to use Ridge**:
- High multicollinearity (VIF > 10)
- p close to n (or p > n)
- Prediction more important than inference
- All predictors potentially relevant

#### Financial Applications

**1. Factor Models**:
```
R_i = Σ βⱼFⱼ + ε
```
When factors are correlated (common in equity factors).

**2. Portfolio Optimization**:
Regularize expected return estimates to prevent extreme weights:
```
w = argmax(w'μ - λ||w||²)
```

**3. Risk Models**:
Estimate factor loadings with many correlated risk factors.

**4. Volatility Forecasting**:
GARCH models with many lags:
```
σ²_t = α₀ + Σ αᵢr²_{t-i} + Σ βⱼσ²_{t-j}
```

**5. High-Frequency Trading**:
Predict returns with many lagged features:
- Prevents overfitting to noise
- More stable predictions

#### Implementation Notes

**Python (scikit-learn)**:
```python
from sklearn.linear_model import Ridge, RidgeCV

# Manual λ
model = Ridge(alpha=1.0)  # alpha = λ
model.fit(X_train, y_train)

# Cross-validated λ
model_cv = RidgeCV(alphas=[0.1, 1.0, 10.0])
model_cv.fit(X_train, y_train)
print(f"Optimal λ: {model_cv.alpha_}")
```

**R**:
```r
library(glmnet)

# Automatic λ selection via CV
cv_fit <- cv.glmnet(X, y, alpha=0)  # alpha=0 for Ridge
lambda_opt <- cv_fit$lambda.min
```

#### Common Pitfalls

1. **Forgetting to standardize**: Leads to scale-dependent penalties
2. **Including intercept in penalty**: Distorts results
3. **Using same λ for all problems**: λ is data-dependent
4. **Interpreting coefficients as causal**: Ridge coefficients are biased
5. **Not using CV**: Training error always decreases with λ

### Lasso Regression (L1 Regularization)

**Objective**:
```
min ||Y - Xβ||² + λ||β||₁
```

Where ||β||₁ = Σ|βⱼ| (L1 norm).

**Key difference from Ridge**:
- **Lasso**: Sets some coefficients exactly to zero (feature selection)
- **Ridge**: Only shrinks toward zero

**Solution**: No closed form; use coordinate descent or LARS algorithm.

#### Lasso vs Ridge

| Property | Ridge | Lasso |
|----------|-------|-------|
| Penalty | L2: Σβⱼ² | L1: Σ\|βⱼ\| |
| Feature selection | No | Yes |
| Coefficients | All non-zero | Some exactly zero |
| Correlated predictors | Includes all | Picks one arbitrarily |
| Interpretability | Lower | Higher (sparse) |

**When to use Lasso**:
- Believe many predictors irrelevant
- Want automatic feature selection
- Need sparse, interpretable model

**When to use Ridge**:
- Believe most predictors relevant
- Predictors highly correlated
- Prediction accuracy paramount

### Elastic Net

**Combines Ridge and Lasso**:
```
min ||Y - Xβ||² + λ₁||β||₁ + λ₂||β||²
```

Or equivalently:
```
min ||Y - Xβ||² + λ[(1-α)||β||² + α||β||₁]
```

Where α ∈ [0, 1] controls Ridge (α=0) vs Lasso (α=1) tradeoff.

**Advantages**:
- Feature selection like Lasso
- Handles correlated predictors like Ridge
- Often outperforms both

**Tuning**: Select both λ and α via cross-validation.

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

## Related Concepts

Understanding how regression concepts interconnect is crucial for hedge fund interviews and practical applications.

### Prerequisites

**Mathematical foundations you need first**:

1. **Linear Algebra** (content/linear_algebra/):
   - Matrix operations: β̂ = (X'X)⁻¹X'Y requires matrix inversion
   - Eigenvalues/eigenvectors: Understanding variance and covariance matrices
   - SVD: Connection to Ridge regression and multicollinearity
   - Projections: OLS as orthogonal projection onto column space of X

2. **Probability Theory** (content/probability/):
   - Random variables: Understanding ε ~ N(0, σ²)
   - Expectation: E[β̂] = β (unbiasedness)
   - Variance: Var(β̂) for inference
   - Distributions: Normal, t, F, χ² for hypothesis testing

3. **Statistics Foundations** (content/statistics/inference.md):
   - Hypothesis testing: t-tests, F-tests
   - Confidence intervals: For regression coefficients
   - Maximum likelihood: Alternative derivation of OLS
   - Sampling distributions: Distribution of β̂

4. **Calculus** (content/calculus/):
   - Optimization: Deriving β̂ by minimizing SSR
   - Partial derivatives: ∂SSR/∂βⱼ = 0
   - Gradients: For regularized regression optimization
   - Taylor series: Understanding approximations

**Concept dependencies**:
```
Linear Algebra (matrices, inverses)
    ↓
Multiple Linear Regression (matrix form)
    ↓
Multicollinearity diagnosis (VIF, condition number)
    ↓
Ridge Regression (regularization)
```

### Applications in Quantitative Finance

**How regression concepts appear in real quant work**:

#### 1. Alpha Generation
**CAPM Regression**:
```
R_portfolio - R_f = α + β(R_market - R_f) + ε
```
- **OLS**: Estimate β (market exposure)
- **Hypothesis testing**: Is α significantly > 0? (skill vs luck)
- **R²**: How much return variance is market-driven?

**Multi-factor alpha**:
- Fama-French, Carhart, custom factors
- Ridge regression when factors are correlated
- Lasso for factor selection

#### 2. Risk Management
**Factor risk models**:
```
R_i = Σ βᵢⱼFⱼ + εᵢ
```
- **Multiple regression**: Estimate factor loadings βᵢⱼ
- **Multicollinearity**: When risk factors overlap (use Ridge)
- **VIF**: Check if factors truly independent
- **Residuals**: Idiosyncratic risk

**Value-at-Risk (VaR)**:
- Regress portfolio returns on risk factors
- Use predicted variance: Var(R_p) = β'Σβ + σ²_ε
- Estimate tail risk from residuals

#### 3. Trading Strategies
**Pairs trading**:
```
S1_t = α + βS2_t + ε_t
```
- **OLS**: Find hedge ratio β
- **Residual analysis**: Test for mean reversion
- **Rolling regression**: Update β over time

**Statistical arbitrage**:
- Multiple regression with many assets
- Ridge/Lasso for high-dimensional predictors
- Cross-validation to prevent overfitting

#### 4. Portfolio Construction
**Optimize mean-variance with estimated returns**:
```
w* = argmax(w'μ̂ - λw'Σw)
```
- **Regression**: Estimate μ̂ from factor models
- **Ridge penalty**: Shrink extreme weights (connects to Ridge regression theory)
- **Bias-variance tradeoff**: Same principle as regularization

**Black-Litterman model**:
- Bayesian regression framework
- Combine market equilibrium (prior) with views (data)
- Ridge regression as Bayesian posterior mean

#### 5. Derivatives Pricing
**Implied volatility modeling**:
```
IV = β₀ + β₁(K/S) + β₂τ + β₃(K/S)² + ε
```
- **Polynomial regression**: Capture volatility smile/skew
- **Diagnostics**: Check residuals for arbitrage opportunities

#### 6. High-Frequency Trading
**Microstructure models**:
```
Δp_t = β₀ + β₁orderflow_t + β₂spread_t + ... + ε_t
```
- **Many predictors**: Lags, order imbalances, depth
- **Ridge/Lasso**: Prevent overfitting to noise
- **Time series regression**: Account for autocorrelation

**Interview connection**: "How would you use regression for market making?"
- Regress price changes on order flow
- Estimate adverse selection cost (β₁)
- Adjust quotes based on predicted price impact

### Extensions and Advanced Topics

**What to learn next after mastering regression**:

#### 1. Time Series Models (content/statistics/time_series.md)
**Why relevant**: Financial data has autocorrelation
- **AR/MA/ARMA**: Extend regression to past values
- **GARCH**: Regression for volatility
- **VAR**: Multivariate time series regression
- **Cointegration**: Long-run equilibrium regression

**Connection**:
```
OLS: Y_t = Xβ + ε_t (ε independent)
    ↓
AR: Y_t = φY_{t-1} + ε_t (ε autocorrelated)
    ↓
ARMA: Y_t = φY_{t-1} + θε_{t-1} + ε_t
```

#### 2. Machine Learning
**Natural progression**:
- **OLS/Ridge/Lasso** → **Neural networks** (non-linear regression)
- **Linear regression** → **Decision trees/Random forests** (handle interactions)
- **Stepwise selection** → **Gradient boosting** (sophisticated feature selection)

**Interview question**: "Why use ML over regression?"
- Regression assumes linearity
- ML captures complex interactions
- But regression more interpretable, better for small data

#### 3. Bayesian Methods
**Bayesian linear regression**:
```
Prior: β ~ N(β₀, Σ₀)
Likelihood: Y|X,β ~ N(Xβ, σ²I)
Posterior: β|Y,X ~ N(β_post, Σ_post)
```

**Connection to Ridge**: Ridge regression = Bayesian regression with Gaussian prior!
```
Ridge penalty λ||β||² ≡ Prior β ~ N(0, σ²/λ I)
```

#### 4. Causal Inference
**Beyond correlation**:
- **Instrumental variables**: When X correlated with ε
- **Difference-in-differences**: Causal effect estimation
- **Regression discontinuity**: Natural experiments

**Interview relevance**: "Your factor model shows correlation. Is it causal?"
- Regression shows association, not causation
- Need theory + proper identification for causal claims

#### 5. Panel Data Methods
**Multiple entities over time**:
```
Y_{it} = β₀ + β₁X_{it} + α_i + γ_t + ε_{it}
```
- **Fixed effects**: Control for unobserved heterogeneity
- **Random effects**: More efficient under assumptions

**Finance application**:
- i = stocks, t = time
- α_i = stock-specific effects
- γ_t = time effects (market conditions)

#### 6. Non-parametric Regression
**Relax linearity assumption**:
- **Kernel regression**: Local averaging
- **Splines**: Piecewise polynomials
- **GAM**: Generalized additive models

**When to use**: Option pricing, volatility surfaces (clearly non-linear)

### Common Hedge Fund Interview Questions

**Technical depth that distinguishes candidates**:

#### Conceptual Questions

**Q1: "Explain the bias-variance tradeoff in Ridge regression."**

**Strong answer**:
- OLS is unbiased but high variance when p ≈ n or multicollinearity present
- Ridge adds bias (shrinks coefficients) but reduces variance significantly
- MSE = Bias² + Variance, optimal λ minimizes MSE
- Example: With severe multicollinearity, OLS variance can be 100x Ridge variance
- Trade small bias for large variance reduction → lower prediction error

**Q2: "Why does Ridge regression solve multicollinearity?"**

**Strong answer**:
- Multicollinearity: X'X near singular → (X'X)⁻¹ unstable
- Ridge: (X'X + λI) always invertible, λ > 0 ensures positive definite
- Geometrically: Adding λI shifts eigenvalues away from zero
- Shrinkage reduces sensitivity to small changes in data
- Coefficients of correlated predictors stabilize (see via Ridge trace)

**Q3: "When would you use Lasso vs Ridge vs Elastic Net?"**

**Strong answer**:
| Scenario | Method | Reason |
|----------|--------|--------|
| All predictors relevant, correlated | Ridge | Keeps all, handles collinearity |
| Most predictors irrelevant | Lasso | Automatic feature selection |
| Many correlated + many irrelevant | Elastic Net | Best of both |
| Need interpretability | Lasso | Sparse model |
| p > n | Ridge/Elastic Net | Lasso unstable |

#### Practical Questions

**Q4: "You're building a factor model with 50 factors. Walk me through your approach."**

**Strong answer**:
1. **Explore multicollinearity**:
   - Compute VIF for each factor
   - Check condition number of X'X
   - Expect high values (factors often correlated)

2. **Consider regularization**:
   - Try Ridge, Lasso, Elastic Net
   - Use cross-validation to select λ (and α for Elastic Net)
   - Compare out-of-sample R²

3. **Standardize predictors**:
   - Essential for regularization
   - Ensures penalty treats all factors equally

4. **Check stability**:
   - Plot Ridge trace: coefficients should stabilize
   - Bootstrap confidence intervals
   - Rolling window validation

5. **Interpret results**:
   - Which factors survive Lasso (most important)?
   - How much do Ridge coefficients shrink?
   - Economic interpretation of signs

**Q5: "Your regression has R² = 0.95 in-sample but 0.40 out-of-sample. What's wrong?"**

**Strong answer**:
- **Overfitting**: Model learned noise, not signal
- **Diagnosis**:
  - Too many predictors relative to n (check p/n ratio)
  - No regularization used
  - Same data for training and testing

- **Solutions**:
  1. Regularization (Ridge/Lasso)
  2. Cross-validation for model selection
  3. Reduce predictors (domain knowledge + stepwise)
  4. Increase sample size
  5. Check for data leakage (future information in predictors)

**Q6: "How do you choose λ in Ridge regression?"**

**Strong answer**:
- **k-fold cross-validation** (gold standard):
  ```
  1. Split data into k folds (k=5 or 10)
  2. For λ in [10⁻⁵, 10⁻⁴, ..., 10²]:
     CV_error(λ) = (1/k)Σ MSE on fold i (trained on other k-1)
  3. λ* = argmin CV_error(λ)
  ```

- **Why not use training error?** Always decreases as λ → 0 (overfits)
- **Why not use test error?** Would overfit to test set
- **Time series**: Use rolling window CV (preserve temporal order)
- **Rule of thumb**: Start with λ around σ̂²/Var(β̂_OLS)

**Q7: "Derive the Ridge regression solution β̂_ridge = (X'X + λI)⁻¹X'Y."**

**Strong answer**:
```
Objective: min ||Y - Xβ||² + λ||β||²

Expand:
= (Y - Xβ)'(Y - Xβ) + λβ'β
= Y'Y - 2β'X'Y + β'X'Xβ + λβ'β

Take derivative w.r.t. β:
∂/∂β = -2X'Y + 2X'Xβ + 2λβ

Set to zero:
-2X'Y + 2X'Xβ + 2λβ = 0
X'Xβ + λβ = X'Y
(X'X + λI)β = X'Y
β̂_ridge = (X'X + λI)⁻¹X'Y
```

**Follow-up**: "Why is this always invertible?"
- X'X is positive semidefinite (eigenvalues ≥ 0)
- λI has eigenvalues λ > 0
- X'X + λI has eigenvalues ≥ λ > 0 → positive definite → invertible

#### Market Application Questions

**Q8: "You're running a pairs trading strategy. The hedge ratio keeps changing. Why, and what do you do?"**

**Strong answer**:
- **Why unstable?**
  - Regime changes (correlation breakdown)
  - Multicollinearity with other pairs
  - Insufficient data (high variance estimate)
  - Non-stationarity

- **Solutions**:
  1. **Rolling window regression**: Update β daily/weekly
  2. **Ridge regression**: Stabilize β with regularization
  3. **Kalman filter**: Time-varying β
  4. **Longer lookback**: Reduce noise but slower adaptation
  5. **Check cointegration**: Ensure long-run relationship exists

**Q9: "Your alpha regression shows α = 2% annually, t-stat = 1.8. Do you have alpha?"**

**Strong answer**:
- **t-stat = 1.8 < 1.96** (5% significance): Cannot reject α = 0
- **p-value ≈ 0.07**: 7% chance observing this if no true alpha
- **Interpretation**: Evidence suggestive but not conclusive

- **Considerations**:
  - **Multiple testing**: If tested 20 strategies, expect 1 false positive
  - **Data snooping**: How much back-testing led to this model?
  - **Economic significance**: 2% may be real but eaten by costs
  - **Out-of-sample**: Does it hold on new data?

- **Decision**: Need more data or out-of-sample validation before deploying capital

**Q10: "How would you build a systematic long-short equity strategy using regression?"**

**Strong answer**:
1. **Factor research**:
   - Identify factors: value, momentum, quality, low vol
   - Regress returns on factors to validate

2. **Factor model**:
   ```
   R_i = α_i + β₁F₁ + β₂F₂ + ... + ε_i
   ```
   - Use Ridge if factors correlated
   - Cross-validation for λ

3. **Signal generation**:
   - Predicted return: R̂_i = Xβ̂
   - Residual alpha: α̂_i = R_i - R̂_i
   - Rank stocks by predicted returns or alphas

4. **Portfolio construction**:
   - Long top quintile, short bottom quintile
   - Weight by signal strength or equal weight
   - Neutralize market exposure (β_portfolio ≈ 0)

5. **Risk management**:
   - Monitor factor exposures (regression diagnostics)
   - Check VIF for multicollinearity in factors
   - Backtest with realistic costs

6. **Ongoing monitoring**:
   - Rolling regression for time-varying betas
   - Check regression assumptions (residuals)
   - Update factor set as markets evolve

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
