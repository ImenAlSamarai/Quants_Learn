---
title: Time Series Analysis
category: statistics
subcategory: time_series
difficulty: 3
---

# Time Series Analysis

Time series analysis studies data collected sequentially over time, essential for forecasting returns, modeling volatility, and understanding temporal dependencies in financial markets.

## Components of Time Series

### Decomposition

```
Y_t = T_t + S_t + C_t + I_t
```

Where:
- T_t: Trend (long-term direction)
- S_t: Seasonality (periodic patterns)
- C_t: Cyclical (non-periodic oscillations)
- I_t: Irregular (random noise)

**Additive** vs **Multiplicative**:
```
Additive: Y_t = T_t + S_t + I_t
Multiplicative: Y_t = T_t × S_t × I_t
```

### Stationarity

A series is **stationary** if:
1. Constant mean: E[Y_t] = μ
2. Constant variance: Var(Y_t) = σ²
3. Autocovariance depends only on lag: Cov(Y_t, Y_{t-k}) = γ_k

**Why important**: Many time series models require stationarity.

**Transformations**:
- Differencing: ΔY_t = Y_t - Y_{t-1}
- Log transform: log(Y_t)
- Log returns: r_t = log(P_t/P_{t-1})

## Autocorrelation

### Autocorrelation Function (ACF)

Correlation between Y_t and Y_{t-k}:
```
ρ_k = Cov(Y_t, Y_{t-k}) / Var(Y_t)
```

**Sample ACF**:
```
r_k = Σ(Y_t - Ȳ)(Y_{t-k} - Ȳ) / Σ(Y_t - Ȳ)²
```

**White noise**: ρ_k = 0 for all k ≠ 0

### Partial Autocorrelation Function (PACF)

Correlation between Y_t and Y_{t-k} after removing effects of intermediate lags.

**Use**: Helps identify AR order.

### Ljung-Box Test

Test H₀: No autocorrelation up to lag m

```
Q = n(n+2) Σ_{k=1}^m [r_k² / (n-k)] ~ χ²_m
```

If Q > critical value, reject H₀ (series is not white noise).

## Autoregressive Models (AR)

### AR(p) Model

```
Y_t = c + φ₁Y_{t-1} + φ₂Y_{t-2} + ... + φₚY_{t-p} + ε_t
```

Where ε_t ~ WN(0, σ²) (white noise).

**Interpretation**: Current value depends on p past values.

### AR(1) Example

```
Y_t = c + φY_{t-1} + ε_t
```

**Stationarity condition**: |φ| < 1

**Mean**: μ = c/(1-φ)

**Variance**: σ²_Y = σ²/(1-φ²)

**ACF**: ρ_k = φ^k (exponential decay)

**PACF**: Cuts off after lag 1

### Identification

**Look at PACF**: Significant spikes indicate AR order.

## Moving Average Models (MA)

### MA(q) Model

```
Y_t = μ + ε_t + θ₁ε_{t-1} + θ₂ε_{t-2} + ... + θ_qε_{t-q}
```

**Interpretation**: Current value is weighted sum of current and past errors.

### MA(1) Example

```
Y_t = μ + ε_t + θε_{t-1}
```

**Mean**: E[Y_t] = μ

**Variance**: Var(Y_t) = σ²(1 + θ²)

**ACF**: ρ₁ = θ/(1+θ²), ρ_k = 0 for k > 1 (cuts off)

**PACF**: Exponential decay

**Invertibility condition**: |θ| < 1

### Identification

**Look at ACF**: Significant spikes indicate MA order.

## ARMA Models

### ARMA(p, q) Model

```
Y_t = c + φ₁Y_{t-1} + ... + φₚY_{t-p} + ε_t + θ₁ε_{t-1} + ... + θ_qε_{t-q}
```

Combines AR and MA components.

### Model Selection

**Box-Jenkins Methodology**:
1. Plot data, check stationarity
2. Transform if needed (difference, log)
3. Examine ACF and PACF
4. Fit candidate models
5. Check residuals (should be white noise)
6. Compare AIC/BIC
7. Forecast

**Information Criteria**:
```
AIC = -2log(L) + 2(p+q+1)
BIC = -2log(L) + log(n)(p+q+1)
```

Lower is better.

## ARIMA Models

### ARIMA(p, d, q)

ARMA model applied to d-differenced series:
```
ΔᵈY_t ~ ARMA(p, q)
```

Where Δ is the differencing operator: ΔY_t = Y_t - Y_{t-1}

**Examples**:
- ARIMA(1,0,0) = AR(1)
- ARIMA(0,1,1) = random walk + MA(1) error
- ARIMA(0,1,0) = random walk

### Random Walk

```
Y_t = Y_{t-1} + ε_t
or
ΔY_t = ε_t
```

**Properties**:
- Non-stationary
- Variance increases over time
- Common model for asset prices

**Random walk with drift**:
```
Y_t = c + Y_{t-1} + ε_t
```

## Volatility Models

### ARCH (Autoregressive Conditional Heteroskedasticity)

ARCH(q) model:
```
r_t = σ_t ε_t
σ²_t = α₀ + α₁r²_{t-1} + ... + α_qr²_{t-q}
```

Where ε_t ~ N(0, 1).

**Captures**: Volatility clustering (high volatility periods cluster together).

### GARCH (Generalized ARCH)

GARCH(p, q) model:
```
r_t = σ_t ε_t
σ²_t = ω + Σα_i r²_{t-i} + Σβ_j σ²_{t-j}
```

**GARCH(1,1)** (most common):
```
σ²_t = ω + αr²_{t-1} + βσ²_{t-1}
```

**Interpretation**:
- α: Reaction to market shocks
- β: Persistence of volatility
- α + β: Persistence of volatility shocks

**Stationarity**: α + β < 1

### Extensions

**EGARCH**: Allows asymmetric response to positive/negative shocks

**GJR-GARCH**: Leverage effect (negative shocks increase volatility more)

**GARCH-M**: Risk premium depends on volatility

## Forecasting

### One-Step-Ahead Forecast

**AR(1)**:
```
Ŷ_{t+1} = c + φY_t
```

**MA(1)**:
```
Ŷ_{t+1} = μ + θε_t
```

### Multi-Step-Ahead Forecast

**AR(1)**:
```
Ŷ_{t+h} = c(1 + φ + ... + φ^{h-1}) + φ^h Y_t
```

As h → ∞: Ŷ_{t+h} → μ = c/(1-φ)

### Forecast Intervals

```
Ŷ_{t+h} ± z_{α/2} · SE(forecast)
```

**Note**: Uncertainty increases with horizon h.

### Evaluating Forecasts

**Mean Squared Error (MSE)**:
```
MSE = (1/n) Σ(Y_t - Ŷ_t)²
```

**Mean Absolute Error (MAE)**:
```
MAE = (1/n) Σ|Y_t - Ŷ_t|
```

**Mean Absolute Percentage Error (MAPE)**:
```
MAPE = (100/n) Σ|Y_t - Ŷ_t|/|Y_t|
```

## Financial Applications

### Returns Modeling

**Stylized facts**:
1. Returns are approximately uncorrelated
2. Squared returns show autocorrelation
3. Volatility clusters
4. Heavy tails (excess kurtosis)
5. Leverage effect

**Common approach**: ARMA for mean + GARCH for volatility

### Volatility Forecasting

```
r_t = μ + σ_t ε_t
σ²_t = ω + αr²_{t-1} + βσ²_{t-1}
```

**One-day-ahead volatility**:
```
σ̂²_{t+1} = ω̂ + α̂r²_t + β̂σ̂²_t
```

**Applications**:
- Option pricing
- VaR calculation
- Portfolio optimization

### Pairs Trading

Test for cointegration:
```
Y_t = α + βX_t + u_t
```

If u_t is stationary (I(0)), Y and X are cointegrated.

**Error Correction Model**:
```
ΔY_t = γ(Y_{t-1} - βX_{t-1}) + ε_t
```

### Market Microstructure

**Intraday patterns**: Seasonality in volume and volatility

**High-frequency data**: AR models for order flow

## Advanced Topics

### Vector Autoregression (VAR)

Multivariate extension:
```
Y_t = c + A₁Y_{t-1} + ... + AₚY_{t-p} + ε_t
```

Where Y_t is a vector.

**Applications**:
- Multiple asset returns
- Macro-financial linkages

### Cointegration

Two non-stationary series are cointegrated if linear combination is stationary.

**Example**: Stock price and futures price

**Engle-Granger test**: Test if residuals from regression are stationary.

### Spectral Analysis

Decompose series into frequency components.

**Applications**: Detecting cyclical patterns

### State Space Models

**Kalman Filter**: Optimal filtering and forecasting

**Applications**: Dynamic beta estimation, trend extraction

## Practice Problems

1. Returns: [0.02, -0.01, 0.03, 0.01, -0.02]. Compute ACF at lags 1 and 2.

2. Fit AR(1): r_t = 0.05 + 0.3r_{t-1} + ε_t. Is it stationary? Find mean.

3. GARCH(1,1): σ²_t = 0.00001 + 0.08r²_{t-1} + 0.90σ²_{t-1}. Is it stationary?

4. Given r₁₀₀ = 0.02 and σ²₁₀₀ = 0.0004, forecast σ²₁₀₁ using GARCH above.

5. Ljung-Box test: n=100, r₁=0.15, r₂=0.10, r₃=0.05. Test at m=3.

## Next Steps

- **Multivariate Time Series**: VAR, VECM, cointegration
- **State Space Models**: Kalman filter, particle filter
- **Machine Learning for Time Series**: LSTM, Prophet
- **High-Frequency Econometrics**: Microstructure, realized volatility
- **Nonlinear Models**: Threshold models, Markov-switching
