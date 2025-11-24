---
title: SVD and Decompositions
category: linear_algebra
subcategory: decomposition
difficulty: 4
estimated_time: 75
---

# Singular Value Decomposition: The Swiss Army Knife of Linear Algebra

Singular Value Decomposition (SVD) is one of the most powerful matrix factorizations. It extends eigendecomposition to non-square matrices and has applications in dimensionality reduction, data compression, recommender systems, and quantitative finance.

## What is SVD?

Every m×n matrix A can be decomposed as:
```
A = UΣVᵀ
```

Where:
- **U** (m×m): Left singular vectors (orthonormal)
- **Σ** (m×n): Diagonal matrix of singular values (σ₁ ≥ σ₂ ≥ ... ≥ 0)
- **Vᵀ** (n×n): Right singular vectors (orthonormal)

**Key insight:** SVD exists for ANY matrix (even non-square, even singular)!

## Relationship to Eigenvalues

The singular values are related to eigenvalues:

**For AᵀA:**
```
AᵀA = (UΣVᵀ)ᵀ(UΣVᵀ) = VΣᵀUᵀUΣVᵀ = VΣ²Vᵀ
```
So V contains eigenvectors of AᵀA, and σᵢ² are the eigenvalues!

**For AAᵀ:**
```
AAᵀ = UΣ²Uᵀ
```
So U contains eigenvectors of AAᵀ.

## Computing SVD

```python
import numpy as np

# Example matrix (stocks × time periods)
A = np.array([
    [0.05, 0.03, 0.08, 0.02],  # Stock 1 returns
    [0.02, 0.04, 0.06, 0.01],  # Stock 2 returns
    [0.04, 0.05, 0.07, 0.03]   # Stock 3 returns
])

# Compute SVD
U, S, Vt = np.linalg.svd(A)

print("Left singular vectors U (stocks space):")
print(U.shape)  # (3, 3)

print("\nSingular values S:")
print(S)  # Array of singular values

print("\nRight singular vectors Vt (time space):")
print(Vt.shape)  # (4, 4)

# Reconstruct A
Sigma = np.zeros((3, 4))
Sigma[:3, :3] = np.diag(S)
A_reconstructed = U @ Sigma @ Vt

print("\nReconstruction error:")
print(np.linalg.norm(A - A_reconstructed))  # Should be very small
```

## Low-Rank Approximation

SVD provides the best low-rank approximation of a matrix:
```
A ≈ Aₖ = Σᵢ₌₁ᵏ σᵢ uᵢvᵢᵀ
```

This minimizes ‖A - Aₖ‖ in the Frobenius norm!

**Applications:**
- Data compression
- Noise reduction
- Feature extraction
- Dimensionality reduction

```python
def low_rank_approximation(A, k):
    """Approximate A with rank-k matrix"""
    U, S, Vt = np.linalg.svd(A, full_matrices=False)

    # Keep only top k singular values
    U_k = U[:, :k]
    S_k = S[:k]
    Vt_k = Vt[:k, :]

    # Reconstruct
    A_k = U_k @ np.diag(S_k) @ Vt_k
    return A_k

# Test with rank-2 approximation
A_k = low_rank_approximation(A, k=2)

print(f"Original matrix shape: {A.shape}")
print(f"Approximation error: {np.linalg.norm(A - A_k):.6f}")

# Variance explained by top-k components
var_explained = S[:2]**2 / (S**2).sum()
print(f"Variance explained by top 2 components: {var_explained.sum():.1%}")
```

## Financial Applications

### 1. Factor Models via SVD

SVD naturally decomposes returns into factors:
```
R = UΣVᵀ = (UΣ)Vᵀ = F × Bᵀ
```

Where:
- F = UΣ: Factor returns (time series)
- Bᵀ = Vᵀ: Factor loadings (how stocks relate to factors)

```python
# Stock returns matrix (stocks × time)
returns = np.random.randn(10, 252)  # 10 stocks, 252 days

# SVD decomposition
U, S, Vt = np.linalg.svd(returns, full_matrices=False)

# Extract top 3 factors
n_factors = 3
factors = U[:, :n_factors] @ np.diag(S[:n_factors])  # Stocks × factors
factor_returns = Vt[:n_factors, :]  # Factors × time

print(f"Factors shape: {factors.shape}")  # (10, 3)
print(f"Factor returns shape: {factor_returns.shape}")  # (3, 252)

# Explained variance by each factor
explained_var = S**2 / (S**2).sum()
print(f"\nVariance explained by top 3 factors: {explained_var[:3].sum():.1%}")

# Reconstruct returns using factors
returns_approx = factors @ factor_returns
reconstruction_error = np.linalg.norm(returns - returns_approx)
print(f"Reconstruction error: {reconstruction_error:.4f}")
```

### 2. Portfolio Construction: Risk Parity

SVD helps identify uncorrelated risk sources for risk parity portfolios:

```python
# Covariance matrix
cov_matrix = np.cov(returns)

# SVD of covariance (or use eigen since it's symmetric)
U, S, Vt = np.linalg.svd(cov_matrix)

# Weights proportional to inverse volatility of principal components
weights = (1 / np.sqrt(S))
weights = weights / weights.sum()  # Normalize

print("Risk parity weights based on principal components:")
print(weights)
```

### 3. Missing Data Imputation

SVD can fill in missing values in return matrices:

```python
def matrix_completion_svd(A, mask, k=2, max_iter=100):
    """
    Complete matrix A where mask indicates observed values
    Uses iterative SVD approximation
    """
    A_filled = A.copy()
    A_filled[~mask] = 0  # Initialize missing values to 0

    for iteration in range(max_iter):
        # Low-rank approximation
        U, S, Vt = np.linalg.svd(A_filled, full_matrices=False)
        A_approx = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]

        # Keep observed values, update missing values
        A_filled[mask] = A[mask]  # Keep observed
        A_filled[~mask] = A_approx[~mask]  # Fill missing

    return A_filled

# Example: Some returns are missing
returns_incomplete = returns.copy()
mask = np.random.rand(*returns.shape) > 0.2  # 20% missing
returns_incomplete[~mask] = np.nan

# Fill in missing values
mask_observed = ~np.isnan(returns_incomplete)
returns_incomplete[~mask_observed] = 0  # Temporary fill for SVD
returns_completed = matrix_completion_svd(returns_incomplete, mask_observed, k=3)

print("Matrix completion via SVD successful!")
```

### 4. Noise Filtering

Financial data is noisy. SVD can separate signal from noise by keeping only top singular values:

```python
def denoise_returns(returns, n_components=5):
    """Remove noise by keeping top n_components"""
    U, S, Vt = np.linalg.svd(returns, full_matrices=False)

    # Zero out small singular values (noise)
    S_filtered = S.copy()
    S_filtered[n_components:] = 0

    # Reconstruct
    returns_denoised = U @ np.diag(S_filtered) @ Vt
    return returns_denoised

# Denoise returns
returns_clean = denoise_returns(returns, n_components=5)

# Compare variance
print(f"Original variance: {returns.var():.6f}")
print(f"Denoised variance: {returns_clean.var():.6f}")
```

### 5. Covariance Matrix Estimation

Random Matrix Theory suggests that smallest eigenvalues of sample covariance matrices are noise. SVD-based shrinkage:

```python
def shrink_covariance_svd(returns, n_factors=5):
    """Shrink covariance matrix using SVD"""
    # Center returns
    returns_centered = returns - returns.mean(axis=1, keepdims=True)

    # SVD
    U, S, Vt = np.linalg.svd(returns_centered, full_matrices=False)

    # Keep top factors
    S_shrunk = S.copy()
    S_shrunk[n_factors:] = S_shrunk[n_factors:].mean()  # Shrink small values

    # Reconstruct covariance
    returns_shrunk = U @ np.diag(S_shrunk) @ Vt
    cov_shrunk = (returns_shrunk @ returns_shrunk.T) / returns_shrunk.shape[1]

    return cov_shrunk

cov_shrunk = shrink_covariance_svd(returns, n_factors=5)
print("Shrunk covariance matrix computed!")
```

## Other Important Decompositions

### QR Decomposition
```
A = QR
```
- Q: Orthogonal matrix
- R: Upper triangular matrix

**Use:** Solving linear systems, least squares

```python
Q, R = np.linalg.qr(A)
print("QR decomposition:")
print(f"Q (orthogonal): {Q.shape}")
print(f"R (upper triangular): {R.shape}")
```

### Cholesky Decomposition
For positive definite matrix A:
```
A = LLᵀ
```
- L: Lower triangular matrix

**Use:** Simulating correlated random variables, efficient solving

```python
# Cholesky decomposition of covariance matrix
cov_matrix = np.array([[1.0, 0.5], [0.5, 1.0]])
L = np.linalg.cholesky(cov_matrix)

print("Cholesky decomposition:")
print(L)

# Generate correlated random variables
n_samples = 1000
uncorrelated = np.random.randn(2, n_samples)
correlated = L @ uncorrelated

print(f"\nTarget correlation:\n{cov_matrix}")
print(f"Achieved correlation:\n{np.cov(correlated)}")
```

**Application:** Monte Carlo simulation of correlated assets!

### LU Decomposition
```
A = LU
```
- L: Lower triangular
- U: Upper triangular

**Use:** Solving systems of equations efficiently

## Practical Example: PCA-Based Trading Strategy

```python
import numpy as np

# Simulate returns for 20 stocks over 500 days
np.random.seed(42)
n_stocks = 20
n_days = 500

# Create factor structure (3 factors + idiosyncratic)
factors = np.random.randn(3, n_days) * 0.01
loadings = np.random.randn(n_stocks, 3)
idiosyncratic = np.random.randn(n_stocks, n_days) * 0.005
returns = loadings @ factors + idiosyncratic

# Apply SVD to identify factors
U, S, Vt = np.linalg.svd(returns, full_matrices=False)

print("=" * 60)
print("PCA-Based Statistical Arbitrage")
print("=" * 60)

# Variance explained
var_explained = S**2 / (S**2).sum()
cumsum_var = np.cumsum(var_explained)

print(f"\nTop 5 components explain {cumsum_var[4]:.1%} of variance")

# Use first 3 PCs to model returns
n_pcs = 3
factors_estimated = U[:, :n_pcs] @ np.diag(S[:n_pcs])
factor_returns = Vt[:n_pcs, :]

# Residuals (unexplained returns) - these mean-revert!
returns_fitted = factors_estimated @ factor_returns
residuals = returns - returns_fitted

print(f"\nResidual standard deviation per stock:")
print(residuals.std(axis=1))

# Trading strategy: Long undervalued, short overvalued
# Based on residuals (deviations from factor model)
latest_residuals = residuals[:, -1]
threshold = 1.5 * residuals.std(axis=1)

# Generate signals
long_signals = latest_residuals < -threshold
short_signals = latest_residuals > threshold

print(f"\nLong positions: {long_signals.sum()}")
print(f"Short positions: {short_signals.sum()}")

# This strategy bets on mean reversion after accounting for factors!
```

## Key Takeaways

1. **SVD works for any matrix** (square, rectangular, singular)
2. **Best low-rank approximation** (optimal for compression/denoising)
3. **Natural for factor models** (decomposes returns into factors × loadings)
4. **Noise filtering** (keep top singular values, discard noise)
5. **σᵢ² = eigenvalues of AᵀA**
6. **Cholesky for correlated simulations**
7. **QR for orthogonalization**

## Comparison: PCA vs SVD

**PCA:**
- Works on covariance matrix (square, symmetric)
- Eigendecomposition: Σ = QΛQᵀ
- Use when you have covariance/correlation matrix

**SVD:**
- Works on data matrix directly (any shape)
- Singular value decomposition: X = UΣVᵀ
- Use when you have raw data matrix

**They're related!**
```
SVD of X ⟺ PCA of XᵀX
```

## Next Steps

You've now completed the core linear algebra curriculum! You're equipped to:
- Understand and implement PCA
- Build factor models
- Construct risk-based portfolios
- Denoise and filter financial data
- Implement dimensionality reduction

**Advanced topics to explore:**
- Random Matrix Theory for covariance cleaning
- Sparse PCA and regularization
- Tensor decompositions
- Non-negative matrix factorization
- Applications in machine learning models
