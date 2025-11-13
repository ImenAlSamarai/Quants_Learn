---
title: Vectors and Vector Spaces
category: linear_algebra
subcategory: vectors
difficulty: 1
estimated_time: 45
---

# Vectors and Vector Spaces

Vectors are the fundamental building blocks of linear algebra. In quantitative finance, vectors represent everything from asset returns to portfolio weights to factor loadings.

## What is a Vector?

A vector is an ordered list of numbers. Geometrically, it represents a point in space or a direction with magnitude.

**Example - Asset Returns:**
```
r = [0.05, 0.03, -0.02, 0.08]
```
This vector represents the monthly returns of four assets: 5%, 3%, -2%, and 8%.

## Vector Operations

### Addition
Vectors of the same dimension can be added element-wise:
```
r₁ = [0.05, 0.03]
r₂ = [0.02, 0.04]
r₁ + r₂ = [0.07, 0.07]
```

**Financial Interpretation:** Combining returns from different time periods or portfolios.

### Scalar Multiplication
Multiplying a vector by a scalar scales all its components:
```
w = [0.4, 0.6]
2w = [0.8, 1.2]
```

**Financial Interpretation:** Leveraging a portfolio position.

### Dot Product (Inner Product)
The dot product of two vectors produces a scalar:
```
a · b = a₁b₁ + a₂b₂ + ... + aₙbₙ
```

**Example - Portfolio Return:**
```python
weights = [0.3, 0.4, 0.3]  # Portfolio weights
returns = [0.05, 0.03, 0.08]  # Asset returns

portfolio_return = weights · returns
                 = 0.3(0.05) + 0.4(0.03) + 0.3(0.08)
                 = 0.051 or 5.1%
```

The dot product calculates the weighted average - the core operation in portfolio return calculation!

## Vector Norms

A norm measures the "size" or "length" of a vector.

### L2 Norm (Euclidean Norm)
```
‖v‖₂ = √(v₁² + v₂² + ... + vₙ²)
```

**Application:** Measuring portfolio risk (volatility), distance between data points.

### L1 Norm (Manhattan Norm)
```
‖v‖₁ = |v₁| + |v₂| + ... + |vₙ|
```

**Application:** Sparse portfolio optimization, reducing transaction costs.

## Vector Spaces

A vector space is a collection of vectors that is closed under addition and scalar multiplication.

**Key Properties:**
1. Contains zero vector
2. Closed under addition: u + v is in the space
3. Closed under scalar multiplication: cv is in the space
4. Associative, commutative, distributive properties hold

**Example - Portfolio Space:**
All possible portfolio weight vectors {w ∈ ℝⁿ : Σwᵢ = 1} form a vector space (with some constraints).

## Linear Independence

Vectors are linearly independent if none can be written as a combination of the others.

**Example:**
```
v₁ = [1, 0]
v₂ = [0, 1]
```
These are independent - neither is a multiple of the other.

```
v₁ = [1, 0]
v₂ = [2, 0]
```
These are dependent - v₂ = 2v₁.

**Financial Application:** Independent risk factors in factor models. We want factors that capture different sources of return, not redundant information.

## Basis and Dimension

A **basis** is a set of linearly independent vectors that span the entire space. The number of vectors in a basis is the **dimension** of the space.

**Example:** For ℝ², the standard basis is:
```
e₁ = [1, 0]
e₂ = [0, 1]
```

Any vector in ℝ² can be written as: v = ae₁ + be₂

**Financial Application:**
- Fama-French 3-factor model uses 3 basis vectors (market, size, value)
- Any stock's excess return can be expressed as a combination of these factors

## Practical Example: Portfolio Optimization Setup

```python
import numpy as np

# Define asset returns (historical)
returns = np.array([0.08, 0.12, 0.06, 0.10])  # 4 assets

# Define portfolio weights (must sum to 1)
weights = np.array([0.25, 0.35, 0.20, 0.20])

# Check weights sum to 1
print(f"Sum of weights: {np.sum(weights)}")  # Should be 1.0

# Calculate portfolio return using dot product
portfolio_return = np.dot(weights, returns)
print(f"Portfolio return: {portfolio_return:.2%}")

# Vector operations
# Increase allocation to stock 1 by 10%
weights_adjusted = weights + np.array([0.10, -0.10, 0, 0])
print(f"Adjusted weights: {weights_adjusted}")
```

## Key Takeaways

1. **Vectors represent data**: Returns, weights, factors, prices
2. **Dot product is everywhere**: Portfolio returns, correlations, projections
3. **Norms measure magnitude**: Risk, distance, size
4. **Linear independence matters**: Avoid redundant information in models
5. **Basis vectors span spaces**: Factor models decompose returns into basis components

## Next Steps

With vectors mastered, you're ready to explore:
- Matrix operations (arrays of vectors)
- Linear transformations (how vectors transform)
- Applications in portfolio theory and factor models
