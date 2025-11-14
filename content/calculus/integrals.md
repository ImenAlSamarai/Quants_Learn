---
title: Integration
category: calculus
subcategory: integrals
difficulty: 2
---

# Integration

Integration is the inverse of differentiation, used to compute accumulated quantities, areas under curves, and expected values in probability. It's essential for pricing derivatives and understanding stochastic processes.

## Fundamental Theorem of Calculus

The two parts connect differentiation and integration:

**Part 1**: If F(x) = ∫ₐˣ f(t) dt, then F'(x) = f(x)

**Part 2**: ∫ₐᵇ f(x) dx = F(b) - F(a), where F'(x) = f(x)

## Integration Techniques

### Basic Rules

```
∫ xⁿ dx = x^(n+1)/(n+1) + C    (n ≠ -1)
∫ 1/x dx = ln|x| + C
∫ eˣ dx = eˣ + C
∫ sin(x) dx = -cos(x) + C
∫ cos(x) dx = sin(x) + C
```

### Substitution (u-substitution)

For ∫ f(g(x))·g'(x) dx:
1. Let u = g(x)
2. Then du = g'(x) dx
3. Integrate ∫ f(u) du
4. Substitute back

**Example**: ∫ 2x·e^(x²) dx
- Let u = x², du = 2x dx
- ∫ eᵘ du = eᵘ + C = e^(x²) + C

### Integration by Parts

```
∫ u dv = uv - ∫ v du
```

**Mnemonic** (LIATE): Choose u in this order:
- Logarithmic
- Inverse trig
- Algebraic
- Trigonometric
- Exponential

**Example**: ∫ x·eˣ dx
- u = x, dv = eˣ dx
- du = dx, v = eˣ
- = x·eˣ - ∫ eˣ dx = x·eˣ - eˣ + C

### Partial Fractions

For rational functions, decompose into simpler fractions:

```
∫ 1/(x²-1) dx = ∫ [1/2(1/(x-1)) - 1/2(1/(x+1))] dx
               = 1/2 ln|x-1| - 1/2 ln|x+1| + C
```

## Definite Integrals

### Properties

1. ∫ₐᵇ f(x) dx = -∫ᵇₐ f(x) dx
2. ∫ₐᵇ f(x) dx + ∫ᵇᶜ f(x) dx = ∫ₐᶜ f(x) dx
3. ∫ₐᵇ [f(x) + g(x)] dx = ∫ₐᵇ f(x) dx + ∫ₐᵇ g(x) dx
4. ∫ₐᵇ c·f(x) dx = c·∫ₐᵇ f(x) dx

### Numerical Integration

When analytical solutions are difficult:

**Trapezoidal Rule**:
```
∫ₐᵇ f(x) dx ≈ (b-a)/2n · [f(x₀) + 2f(x₁) + ... + 2f(xₙ₋₁) + f(xₙ)]
```

**Simpson's Rule**:
```
∫ₐᵇ f(x) dx ≈ (b-a)/3n · [f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + f(xₙ)]
```

**Monte Carlo Integration**:
```
∫ₐᵇ f(x) dx ≈ (b-a)/N · Σf(xᵢ)    where xᵢ ~ U(a,b)
```

## Applications in Finance

### Present Value

Continuous discounting:
```
PV = ∫₀ᵀ CF(t)·e^(-rt) dt
```

### Expected Values

For continuous random variables:
```
E[X] = ∫₋∞^∞ x·f(x) dx
```

Where f(x) is the probability density function.

### Option Pricing

Black-Scholes formula involves integrating the normal distribution:
```
C = S·N(d₁) - K·e^(-rT)·N(d₂)
```

Where N(x) = ∫₋∞ˣ (1/√(2π))·e^(-t²/2) dt

### Risk-Neutral Pricing

```
V = e^(-rT)·∫₀^∞ max(S-K, 0)·f(S) dS
```

### Duration and Convexity

Bond duration (sensitivity to interest rates):
```
D = (1/P)·∫₀ᵀ t·CF(t)·e^(-rt) dt
```

## Improper Integrals

### Type 1: Infinite Limits

```
∫₁^∞ 1/x² dx = lim(b→∞) ∫₁ᵇ 1/x² dx = lim(b→∞) [-1/x]₁ᵇ = 1
```

### Type 2: Discontinuous Integrand

```
∫₀¹ 1/√x dx = lim(a→0⁺) ∫ₐ¹ 1/√x dx = 2
```

## Practice Problems

1. Evaluate: ∫ x²·sin(x) dx (integration by parts)
2. Compute: ∫₀^π sin²(x) dx
3. Find: ∫ (3x+5)/(x²+x-2) dx (partial fractions)
4. Calculate expected value: E[X] where X ~ Exp(λ)

## Next Steps

- **Multivariable Calculus**: Double and triple integrals
- **Differential Equations**: Using integration to solve DEs
- **Probability**: Computing expectations and probabilities
- **Stochastic Calculus**: Ito integrals for continuous-time finance
