---
title: Eigenvalues and Eigenvectors
category: linear_algebra
subcategory: eigenvalues
difficulty: 3
estimated_time: 60
---

# Eigenvalues and Eigenvectors: Uncovering Hidden Structure

Eigenvalues and eigenvectors reveal the intrinsic properties of a matrix. They are fundamental to understanding covariance matrices, PCA, PageRank, quantum mechanics, and countless applications in quantitative finance.

## Definition

For a square matrix A, an **eigenvector** v is a non-zero vector that satisfies:
```
Av = λv
```

where λ (lambda) is the corresponding **eigenvalue**.

**Key insight:** The transformation A only *scales* v by λ, without changing its direction.

## Geometric Intuition

Most vectors change both magnitude AND direction when transformed by A. Eigenvectors are special - they only change in magnitude (by factor λ).

**Example:**
```python
import numpy as np

A = np.array([[3, 1], [0, 2]])

# This is an eigenvector with eigenvalue 3
v1 = np.array([1, 0])
print(A @ v1)  # [3, 0] = 3 * [1, 0]

# This is an eigenvector with eigenvalue 2
v2 = np.array([1, 1])
print(A @ v2)  # [4, 2] ≠ 2 * [1, 1]  Wait, let me recalculate...

# Actually, let's find the real eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"Eigenvalues: {eigenvalues}")     # [3, 2]
print(f"Eigenvectors:\n{eigenvectors}")
```

## Finding Eigenvalues and Eigenvectors

### The Characteristic Equation

To find eigenvalues, solve:
```
det(A - λI) = 0
```

This is called the **characteristic polynomial**.

**Example - 2×2 Matrix:**
```
A = | 4  1 |
    | 2  3 |

A - λI = | 4-λ    1  |
         |  2   3-λ  |

det(A - λI) = (4-λ)(3-λ) - 2 = λ² - 7λ + 10 = 0

Solving: λ₁ = 5, λ₂ = 2
```

For each eigenvalue, solve (A - λI)v = 0 to find the eigenvector.

### Properties of Eigenvalues

1. **Trace = sum of eigenvalues:** tr(A) = Σᵢ λᵢ
2. **Determinant = product of eigenvalues:** det(A) = Πᵢ λᵢ
3. **Eigenvalues of A⁻¹ are 1/λᵢ**
4. **Eigenvalues of Aᵏ are λᵢᵏ**

## Diagonalization

A matrix A is **diagonalizable** if there exists an invertible matrix P such that:
```
A = PDP⁻¹
```

where D is diagonal with eigenvalues on the diagonal, and P has eigenvectors as columns.

**Power of diagonalization:**
```
Aᵏ = PD ᵏP⁻¹
```

Computing Dᵏ is trivial (just raise diagonal elements to power k)!

## Symmetric Matrices: The Gold Standard

Symmetric matrices (A = Aᵀ) have special properties:

1. **All eigenvalues are real** (no complex numbers)
2. **Eigenvectors are orthogonal** (perpendicular)
3. **Always diagonalizable**

**Spectral theorem:**
```
A = QΛQᵀ
```

where Q has orthonormal eigenvectors and Λ is diagonal.

**Why this matters:** Covariance matrices are symmetric!

## Financial Applications

### 1. Principal Component Analysis (PCA)

PCA finds the directions of maximum variance in data. The eigenvectors of the covariance matrix are the principal components!

```python
import numpy as np

# Covariance matrix of asset returns
Sigma = np.array([
    [0.04, 0.02, 0.01],
    [0.02, 0.03, 0.015],
    [0.01, 0.015, 0.025]
])

# Eigendecomposition
eigenvalues, eigenvectors = np.linalg.eig(Sigma)

# Sort by importance
idx = eigenvalues.argsort()[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

print("Variance explained by each component:")
variance_explained = eigenvalues / eigenvalues.sum()
print(variance_explained)

print("\nFirst principal component (direction of max variance):")
print(eigenvectors[:, 0])

# Often, first 2-3 components explain 80-90% of variance!
print(f"\nFirst 2 components explain {variance_explained[:2].sum():.1%} of variance")
```

**Applications:**
- Risk factor identification
- Dimensionality reduction
- Portfolio construction (risk-based)

### 2. Risk Decomposition

The total portfolio variance can be decomposed using eigenvalues:
```
Total variance = Σᵢ λᵢ
```

Each eigenvalue represents variance along a principal component (independent risk factor).

```python
# Portfolio risk decomposition
total_variance = eigenvalues.sum()
print("Risk decomposition:")
for i, (λ, pct) in enumerate(zip(eigenvalues, variance_explained)):
    print(f"  Component {i+1}: {λ:.4f} ({pct:.1%})")
```

**Insight:** If one eigenvalue dominates (λ₁ >> others), portfolio risk is concentrated in one direction - potentially risky!

### 3. Minimum Variance Portfolio

The eigenvector corresponding to the smallest eigenvalue points to the direction of minimum variance.

```python
# Minimum variance direction
min_variance_direction = eigenvectors[:, -1]  # Last eigenvector
min_variance = eigenvalues[-1]

print(f"Minimum variance direction: {min_variance_direction}")
print(f"Minimum variance: {min_variance:.4f}")
```

### 4. Sharpe Ratio Optimization

The maximum Sharpe ratio portfolio can be found using eigenvalue methods for certain problems.

### 5. Correlation Matrix Analysis

Eigenvalues of correlation matrices reveal dependencies:
- All eigenvalues > 0 (positive semi-definite)
- Trace = number of variables
- Large first eigenvalue → high correlation among assets
- Many small eigenvalues → diversification potential

```python
# Correlation matrix analysis
correlation_matrix = np.corrcoef(np.random.randn(100, 5).T)
eigenvalues_corr, _ = np.linalg.eig(correlation_matrix)

print("Correlation eigenvalues:")
print(eigenvalues_corr)
print(f"Sum (should be 5): {eigenvalues_corr.sum():.2f}")

# If first eigenvalue is close to n, assets are highly correlated
print(f"First eigenvalue / n = {eigenvalues_corr[0] / 5:.2f}")
# Close to 1.0 means everything is correlated (bad for diversification!)
```

## Power Method: Finding Dominant Eigenvalue

The power method iteratively finds the largest eigenvalue:

```python
def power_method(A, num_iterations=100):
    """Find largest eigenvalue and eigenvector"""
    n = A.shape[0]
    v = np.random.rand(n)  # Random starting vector

    for _ in range(num_iterations):
        # Multiply by A
        v_new = A @ v

        # Normalize
        v_new = v_new / np.linalg.norm(v_new)
        v = v_new

    # Compute eigenvalue (Rayleigh quotient)
    eigenvalue = (v.T @ A @ v) / (v.T @ v)

    return eigenvalue, v

# Test it
A = np.array([[4, 1], [2, 3]])
λ, v = power_method(A)
print(f"Largest eigenvalue: {λ:.4f}")
print(f"Corresponding eigenvector: {v}")

# Compare with numpy
true_λ, _ = np.linalg.eig(A)
print(f"True largest eigenvalue: {max(true_λ):.4f}")
```

**Application:** Google's PageRank algorithm uses the power method on a huge matrix!

## Practical Example: Building a PCA-Based Portfolio

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate 5 correlated asset returns
np.random.seed(42)
n_assets = 5
n_periods = 252  # 1 year of daily returns

# Create correlated returns
mean_returns = np.array([0.08, 0.10, 0.07, 0.09, 0.11]) / 252  # Daily
factor = np.random.randn(n_periods, 1)  # Common factor
idiosyncratic = np.random.randn(n_periods, n_assets) * 0.01  # Idiosyncratic
returns = factor @ np.ones((1, n_assets)) * 0.02 + idiosyncratic + mean_returns

# Covariance matrix
cov_matrix = np.cov(returns.T)

# PCA
eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
idx = eigenvalues.argsort()[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

print("=" * 60)
print("PCA Analysis")
print("=" * 60)

# Variance explained
var_explained = eigenvalues / eigenvalues.sum()
cum_var_explained = np.cumsum(var_explained)

print("\nVariance explained:")
for i, (var, cum_var) in enumerate(zip(var_explained, cum_var_explained)):
    print(f"  PC{i+1}: {var:.1%} (cumulative: {cum_var:.1%})")

# Construct portfolios using principal components
pc1_portfolio = eigenvectors[:, 0]
pc1_portfolio = pc1_portfolio / pc1_portfolio.sum()  # Normalize to sum to 1

print(f"\nPC1 Portfolio weights:")
for i, w in enumerate(pc1_portfolio):
    print(f"  Asset {i+1}: {w:.1%}")

# Compare variance
pc1_returns = returns @ pc1_portfolio
equal_weight = np.ones(n_assets) / n_assets
equal_returns = returns @ equal_weight

print(f"\nPC1 Portfolio volatility: {np.std(pc1_returns):.2%}")
print(f"Equal-weight volatility: {np.std(equal_returns):.2%}")
```

## Advanced: Eigenvalue Sensitivity

Eigenvalues can be sensitive to small changes in the matrix (especially for non-symmetric matrices). For covariance estimation:

- Use shrinkage estimators (Ledoit-Wolf)
- Random Matrix Theory can help identify spurious eigenvalues
- Consider robust covariance estimation

## Key Takeaways

1. **Eigenvectors = natural directions** of a transformation
2. **Eigenvalues = scaling factors** along those directions
3. **Symmetric matrices have orthogonal eigenvectors** (covariance matrices!)
4. **PCA = eigendecomposition of covariance matrix**
5. **Sum of eigenvalues = total variance**
6. **Large first eigenvalue = high correlation** (limited diversification)
7. **Trace = sum of eigenvalues**, **det = product of eigenvalues**

## Next Steps

With eigenvalues mastered, you're ready for:
- Singular Value Decomposition (SVD) - eigenvalues for non-square matrices
- Advanced PCA techniques
- Factor models and factor risk decomposition
- Spectral risk measures
