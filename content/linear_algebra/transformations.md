---
title: Linear Transformations
category: linear_algebra
subcategory: transformations
difficulty: 3
estimated_time: 50
---

# Linear Transformations: The Geometric Heart of Linear Algebra

A linear transformation is a function between vector spaces that preserves vector addition and scalar multiplication. Every matrix represents a linear transformation, and understanding this connection unlocks powerful geometric intuition.

## Definition

A function T: ℝⁿ → ℝᵐ is a linear transformation if for all vectors u, v and scalar c:

1. **Additivity:** T(u + v) = T(u) + T(v)
2. **Homogeneity:** T(cu) = cT(u)

**In practice:** T(v) = Av for some matrix A.

## Matrix as Transformation

Every m×n matrix A defines a linear transformation from ℝⁿ to ℝᵐ:
```
T(x) = Ax
```

The columns of A tell you where the basis vectors go:
```
A = [T(e₁) | T(e₂) | ... | T(eₙ)]
```

### Example: 2D Rotation

Rotating vectors by θ counterclockwise:
```
R(θ) = | cos θ  -sin θ |
       | sin θ   cos θ |
```

**Application:**
```python
import numpy as np

theta = np.pi / 4  # 45 degrees
R = np.array([
    [np.cos(theta), -np.sin(theta)],
    [np.sin(theta),  np.cos(theta)]
])

v = np.array([1, 0])  # Vector pointing right
rotated = R @ v
print(f"After 45° rotation: {rotated}")  # [0.707, 0.707]
```

## Common Transformations

### 1. Scaling
Stretch or shrink along axes:
```
S = | sx   0  |
    | 0   sy  |
```

### 2. Reflection
Flip across a line or plane:
```
# Reflection across x-axis
Rx = | 1   0 |
     | 0  -1 |

# Reflection across line y=x
R₄₅ = | 0  1 |
      | 1  0 |
```

### 3. Shear
Tilt along one direction:
```
Shear_x = | 1  k |
          | 0  1 |
```

### 4. Projection
Project onto a subspace:
```
# Project onto x-axis
Px = | 1  0 |
     | 0  0 |
```

## Composition of Transformations

Applying transformations in sequence corresponds to matrix multiplication:
```
T₂(T₁(v)) = B(Av) = (BA)v
```

**Order matters!** BA ≠ AB in general.

**Example:**
```python
# Rotate then scale
rotation = np.array([[0, -1], [1, 0]])  # 90° rotation
scaling = np.array([[2, 0], [0, 3]])    # Scale x by 2, y by 3

# Compose: first rotate, then scale
composed = scaling @ rotation
print(composed)

# Different order gives different result!
composed_reverse = rotation @ scaling
print(composed_reverse)
```

## Range and Null Space

### Range (Column Space)
The set of all possible outputs: Range(A) = {Av : v ∈ ℝⁿ}

**Geometric meaning:** What subspace can the transformation reach?

### Null Space (Kernel)
The set of vectors that map to zero: Null(A) = {v : Av = 0}

**Geometric meaning:** What gets "collapsed" to the origin?

**Example:**
```
A = | 1  2 |
    | 2  4 |

# Null space: vectors proportional to [-2, 1]
# These get mapped to zero!
```

**Rank-Nullity Theorem:**
```
dim(Range(A)) + dim(Null(A)) = n
```

## Financial Applications

### 1. Portfolio Rebalancing
Transform current weights to target weights:
```python
# Current weights
w_current = np.array([0.5, 0.3, 0.2])

# Target transformation matrix
T = np.array([
    [0.8, 0.1, 0.1],  # Asset 1 target composition
    [0.1, 0.7, 0.2],  # Asset 2 target composition
    [0.1, 0.2, 0.7]   # Asset 3 target composition
])

w_target = T @ w_current
```

### 2. Risk Factor Mapping
Transform individual stock returns to factor exposures:
```
factor_returns = B × stock_returns
```

Where B is the factor loading matrix.

### 3. Change of Basis in Factor Models

Factor models use a change of basis to represent returns:
```
R = α + Bf + ε
```

Where:
- R: stock returns (original basis)
- B: transformation matrix (factor loadings)
- f: factor returns (new basis)

**Example - Fama-French 3-Factor:**
```python
# Factor loadings matrix (N stocks × 3 factors)
B = np.array([
    [1.2, 0.8, -0.3],  # Stock 1: high market beta, growth stock
    [0.9, -0.4, 0.6],  # Stock 2: value stock
    [1.1, 0.2, 0.1]    # Stock 3: balanced
])

# Factor returns [MKT, SMB, HML]
factors = np.array([0.05, 0.02, 0.01])

# Transform factor returns to stock returns
stock_returns = B @ factors
print(f"Stock returns from factors: {stock_returns}")
```

## Eigenvalue Preview

Some special vectors don't change direction under transformation:
```
Av = λv
```

These **eigenvectors** only get scaled by **eigenvalue** λ.

**Geometric intuition:** These are the "natural directions" of the transformation.

**Example - Covariance Matrix:**
```python
import numpy as np

# Sample covariance matrix
Sigma = np.array([
    [4, 2],
    [2, 3]
])

# Find eigenvectors (principal components!)
eigenvalues, eigenvectors = np.linalg.eig(Sigma)

print("Eigenvalues (variance along principal components):")
print(eigenvalues)

print("\nEigenvectors (principal component directions):")
print(eigenvectors)

# First eigenvector is the direction of maximum variance
pc1 = eigenvectors[:, 0]
print(f"\nFirst principal component direction: {pc1}")
```

## Invertible Transformations

A transformation is invertible if there exists T⁻¹ such that:
```
T⁻¹(T(v)) = v  for all v
```

**Requirements:**
1. Must be square (n → n)
2. det(A) ≠ 0
3. Columns are linearly independent
4. Null space is just {0}

**Financial meaning:** Can uniquely reverse the transformation (like unwinding a hedge).

## Practical Example: PCA Transformation

Principal Component Analysis finds the transformation that decorrelates returns:

```python
import numpy as np

# Historical returns for 3 correlated assets
returns = np.random.multivariate_normal(
    mean=[0.05, 0.04, 0.06],
    cov=[[0.04, 0.02, 0.01],
         [0.02, 0.03, 0.015],
         [0.01, 0.015, 0.025]],
    size=100
)

# Center the data
returns_centered = returns - returns.mean(axis=0)

# Covariance matrix
cov = np.cov(returns_centered.T)

# Eigendecomposition
eigenvalues, eigenvectors = np.linalg.eig(cov)

# Sort by eigenvalue (most important first)
idx = eigenvalues.argsort()[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Transform to principal components
pc_returns = returns_centered @ eigenvectors

print("Original correlation:")
print(np.corrcoef(returns_centered.T))

print("\nPrincipal component correlation (uncorrelated!):")
print(np.corrcoef(pc_returns.T))

print("\nVariance explained:")
print(eigenvalues / eigenvalues.sum())
```

## Key Takeaways

1. **Matrices are transformations**: Geometric interpretation provides intuition
2. **Composition = multiplication**: Chaining transformations = multiplying matrices
3. **Basis matters**: Changing basis can simplify problems (factor models, PCA)
4. **Range and null space**: What the transformation reaches and what it collapses
5. **Eigenvectors are special**: Directions preserved by the transformation

## Next Steps

You're now ready to dive deep into:
- Eigenvalues and eigenvectors (the special directions)
- Diagonalization (simplifying transformations)
- Applications in PCA, factor models, and risk decomposition
