---
title: Limits and Continuity
category: calculus
subcategory: limits
difficulty: 1
---

# Limits and Continuity

Limits are the fundamental building block of calculus, describing the behavior of functions as inputs approach specific values. Understanding limits is essential for derivatives, integrals, and analyzing function behavior.

## What is a Limit?

The limit of f(x) as x approaches a is the value that f(x) gets arbitrarily close to as x gets close to a:

```
lim (x→a) f(x) = L
```

This means that f(x) can be made arbitrarily close to L by making x sufficiently close to a.

## Key Concepts

### One-Sided Limits

- **Left-hand limit**: lim (x→a⁻) f(x) - approaching from values less than a
- **Right-hand limit**: lim (x→a⁺) f(x) - approaching from values greater than a

For a limit to exist, both one-sided limits must exist and be equal.

### Continuity

A function f is continuous at point a if:
1. f(a) exists
2. lim (x→a) f(x) exists
3. lim (x→a) f(x) = f(a)

Intuitively, you can draw the function without lifting your pen.

### Limit Laws

1. **Sum**: lim [f(x) + g(x)] = lim f(x) + lim g(x)
2. **Product**: lim [f(x) · g(x)] = lim f(x) · lim g(x)
3. **Quotient**: lim [f(x) / g(x)] = lim f(x) / lim g(x), if lim g(x) ≠ 0
4. **Power**: lim [f(x)]ⁿ = [lim f(x)]ⁿ

## Important Limits

### Standard Limits

```
lim (x→0) sin(x)/x = 1
lim (x→∞) (1 + 1/x)ˣ = e
lim (x→0) (1 + x)^(1/x) = e
lim (x→0) (eˣ - 1)/x = 1
```

### L'Hôpital's Rule

When faced with indeterminate forms (0/0 or ∞/∞), L'Hôpital's rule states:

```
lim (x→a) f(x)/g(x) = lim (x→a) f'(x)/g'(x)
```

## Applications in Finance

### Option Pricing Limits

As time to expiration approaches zero, option values converge to their intrinsic value:

```
lim (T→0) C(S, T) = max(S - K, 0)
```

### Delta Hedging

The delta of an option is defined as a limit:

```
Δ = lim (ΔS→0) ΔC/ΔS = ∂C/∂S
```

### Continuous Compounding

The limit definition of e leads to continuous compounding:

```
FV = PV × lim (n→∞) (1 + r/n)^(n×t) = PV × e^(r×t)
```

## Practice Problems

1. Calculate: lim (x→2) (x² - 4)/(x - 2)
2. Determine if f(x) = |x|/x is continuous at x = 0
3. Use L'Hôpital's rule: lim (x→0) (sin(x) - x)/x³

## Next Steps

After mastering limits, you'll be ready to study:
- **Derivatives**: Using limits to define instantaneous rates of change
- **Integration**: Using limits of Riemann sums
- **Series**: Using limits to determine convergence
