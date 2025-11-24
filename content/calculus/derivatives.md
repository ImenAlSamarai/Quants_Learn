---
title: Derivatives
category: calculus
subcategory: derivatives
difficulty: 2
---

# Derivatives

The derivative measures the instantaneous rate of change of a function. It's fundamental to optimization, sensitivity analysis, and understanding how quantities change in finance and machine learning.

## Definition

The derivative of f at point x is defined as:

```
f'(x) = lim (h→0) [f(x + h) - f(x)] / h
```

This represents the slope of the tangent line to f at x.

## Derivative Rules

### Basic Rules

1. **Power Rule**: d/dx [xⁿ] = n·xⁿ⁻¹
2. **Constant Multiple**: d/dx [c·f(x)] = c·f'(x)
3. **Sum Rule**: d/dx [f(x) + g(x)] = f'(x) + g'(x)
4. **Product Rule**: d/dx [f(x)·g(x)] = f'(x)·g(x) + f(x)·g'(x)
5. **Quotient Rule**: d/dx [f(x)/g(x)] = [f'(x)·g(x) - f(x)·g'(x)] / [g(x)]²
6. **Chain Rule**: d/dx [f(g(x))] = f'(g(x))·g'(x)

### Common Derivatives

```
d/dx [eˣ] = eˣ
d/dx [ln(x)] = 1/x
d/dx [sin(x)] = cos(x)
d/dx [cos(x)] = -sin(x)
d/dx [tan(x)] = sec²(x)
```

## Higher Order Derivatives

- **Second derivative** f''(x): Rate of change of the rate of change (concavity)
- **Third derivative** f'''(x): Rate of change of concavity
- **nth derivative** f⁽ⁿ⁾(x): Generalization to any order

## Applications in Optimization

### Finding Extrema

To find local maxima and minima:
1. Find critical points: f'(x) = 0
2. Use second derivative test:
   - f''(x) > 0 → local minimum
   - f''(x) < 0 → local maximum
   - f''(x) = 0 → inconclusive

### Newton's Method

Numerical root-finding algorithm:

```
x_(n+1) = x_n - f(x_n)/f'(x_n)
```

## Financial Applications

### The Greeks

In options pricing, Greeks are partial derivatives measuring sensitivities:

- **Delta (Δ)**: ∂V/∂S - sensitivity to underlying price
- **Gamma (Γ)**: ∂²V/∂S² - rate of change of delta
- **Vega (ν)**: ∂V/∂σ - sensitivity to volatility
- **Theta (Θ)**: ∂V/∂t - time decay
- **Rho (ρ)**: ∂V/∂r - sensitivity to interest rates

### Portfolio Optimization

Finding optimal weights by setting gradient to zero:

```
∂/∂w [w'Σw - λw'μ] = 0
```

### Machine Learning

Gradient descent updates parameters using derivatives:

```
θ_(t+1) = θ_t - α·∇L(θ_t)
```

Where ∇L is the gradient (vector of partial derivatives) of the loss function.

## Implicit Differentiation

For equations where y is defined implicitly (e.g., x² + y² = 1):

```
d/dx [x² + y²] = d/dx [1]
2x + 2y·dy/dx = 0
dy/dx = -x/y
```

## Logarithmic Differentiation

Useful for products and quotients:

```
y = x^x
ln(y) = x·ln(x)
1/y · dy/dx = ln(x) + 1
dy/dx = x^x · (ln(x) + 1)
```

## Practice Problems

1. Find dy/dx for y = x³·e^(2x)
2. Use implicit differentiation: x² + xy + y² = 7
3. Optimize: f(x) = -x² + 4x + 3
4. Calculate Delta for a call option: C = S·N(d₁) - K·e^(-rt)·N(d₂)

## Next Steps

- **Integration**: The inverse operation of differentiation
- **Multivariable Calculus**: Partial derivatives and gradients
- **Differential Equations**: Equations involving derivatives
- **Optimization**: Advanced techniques using derivatives
