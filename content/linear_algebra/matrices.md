---
title: Matrix Operations
category: linear_algebra
subcategory: matrices
difficulty: 2
estimated_time: 60
---

# Matrix Operations: The Engine of Quantitative Finance

Matrices are rectangular arrays of numbers that represent linear transformations, systems of equations, and relationships between variables. In finance, matrices are everywhere: covariance matrices, transition probabilities, factor loadings, and more.

## What is a Matrix?

A matrix is a 2D array of numbers with m rows and n columns (m × n matrix).

**Example - Returns Matrix:**
```
R = | 0.05  0.03  0.08 |  ← Stock 1 returns over 3 periods
    | 0.02  0.04  0.06 |  ← Stock 2 returns over 3 periods
    | 0.03  0.05  0.07 |  ← Stock 3 returns over 3 periods
```

Rows represent different stocks, columns represent time periods (or vice versa).

## Basic Matrix Operations

### Transpose
Flip rows and columns: Aᵀ where (Aᵀ)ᵢⱼ = Aⱼᵢ

```
A = | 1  2  3 |       Aᵀ = | 1  4 |
    | 4  5  6 |            | 2  5 |
                            | 3  6 |
```

**Application:** Converting row vectors to column vectors, transposing data matrices.

### Matrix Addition
Element-wise addition (matrices must have same dimensions):
```
A + B = | a₁₁+b₁₁  a₁₂+b₁₂ |
        | a₂₁+b₂₁  a₂₂+b₂₂ |
```

### Scalar Multiplication
Multiply every element by a scalar:
```
cA = | ca₁₁  ca₁₂ |
     | ca₂₁  ca₂₂ |
```

## Matrix Multiplication

The most important operation! For A (m×n) and B (n×p), the product AB is (m×p):
```
(AB)ᵢⱼ = Σₖ aᵢₖ bₖⱼ
```

**Key insight:** Each element is the dot product of a row of A and a column of B.

**Example:**
```
A = | 1  2 |    B = | 5  6 |
    | 3  4 |        | 7  8 |

AB = | 1(5)+2(7)  1(6)+2(8) | = | 19  22 |
     | 3(5)+4(7)  3(6)+4(8) |   | 43  50 |
```

**Important:** Matrix multiplication is NOT commutative: AB ≠ BA in general.

### Financial Application: Portfolio Variance

The variance of a portfolio is computed using matrix multiplication:
```
σₚ² = wᵀ Σ w
```

Where:
- w is the weight vector (n×1)
- Σ is the covariance matrix (n×n)
- wᵀ is the transpose (1×n)

**Example:**
```python
import numpy as np

# Two assets
weights = np.array([[0.6], [0.4]])  # 60% stock, 40% bond

# Covariance matrix (variances on diagonal, covariances off-diagonal)
cov_matrix = np.array([
    [0.04, 0.01],   # Stock variance: 4%, covariance: 1%
    [0.01, 0.02]    # Bond variance: 2%
])

# Portfolio variance: wᵀ Σ w
portfolio_variance = weights.T @ cov_matrix @ weights
portfolio_volatility = np.sqrt(portfolio_variance[0, 0])

print(f"Portfolio variance: {portfolio_variance[0, 0]:.4f}")
print(f"Portfolio volatility: {portfolio_volatility:.2%}")
```

## Special Matrices

### Identity Matrix (I)
A square matrix with 1s on the diagonal and 0s elsewhere:
```
I₃ = | 1  0  0 |
     | 0  1  0 |
     | 0  0  1 |
```

**Property:** AI = IA = A (identity element for multiplication)

### Zero Matrix
All elements are zero. Additive identity: A + 0 = A

### Diagonal Matrix
Non-zero elements only on the diagonal:
```
D = | λ₁  0   0  |
    | 0   λ₂  0  |
    | 0   0   λ₃ |
```

**Application:** Scaling transformations, eigenvalue matrices.

### Symmetric Matrix
A matrix equal to its transpose: A = Aᵀ

**Example - Covariance Matrix:**
```
Σ = | σ₁²      σ₁₂ |
    | σ₁₂      σ₂² |
```

Covariance matrices are always symmetric because Cov(X,Y) = Cov(Y,X).

## Matrix Inverse

For a square matrix A, the inverse A⁻¹ (if it exists) satisfies:
```
A A⁻¹ = A⁻¹ A = I
```

**Not all matrices have inverses!** A matrix is invertible if:
- It's square
- Its determinant is non-zero
- Its columns are linearly independent

### 2×2 Inverse Formula:
```
A = | a  b |       A⁻¹ = 1/(ad-bc) | d  -b |
    | c  d |                        |-c   a |
```

**Example:**
```
A = | 2  1 |
    | 3  4 |

det(A) = 2(4) - 1(3) = 5

A⁻¹ = 1/5 | 4  -1 | = | 0.8  -0.2 |
          |-3   2 |   |-0.6   0.4 |
```

### Financial Application: Solving for Portfolio Weights

Given expected returns and a target return, solve for weights:
```
Aw = b  ⟹  w = A⁻¹b
```

**Example - Long-short portfolio:**
```python
import numpy as np

# Constraint matrix: [sum_of_weights, weighted_return]
A = np.array([
    [1, 1],      # w₁ + w₂ = 1
    [0.08, 0.12] # 0.08w₁ + 0.12w₂ = target
])

# Target constraints
b = np.array([1, 0.10])  # Sum to 1, target 10% return

# Solve for weights
weights = np.linalg.solve(A, b)
print(f"Weights: {weights}")  # [0.5, 0.5]
```

## Determinant

The determinant is a scalar value that encodes information about the matrix:
- det(A) = 0 ⟹ matrix is singular (not invertible)
- det(A) ≠ 0 ⟹ matrix is invertible

**2×2 Determinant:**
```
det | a  b | = ad - bc
    | c  d |
```

**Properties:**
1. det(AB) = det(A) det(B)
2. det(Aᵀ) = det(A)
3. det(A⁻¹) = 1/det(A)

**Geometric interpretation:** The determinant represents the volume scaling factor of the linear transformation.

## Trace

The trace is the sum of diagonal elements:
```
tr(A) = Σᵢ aᵢᵢ
```

**Properties:**
1. tr(A + B) = tr(A) + tr(B)
2. tr(AB) = tr(BA) (cyclic property)
3. tr(Aᵀ) = tr(A)

**Financial Application:**
The trace of a covariance matrix equals the total variance across all assets:
```python
total_variance = np.trace(cov_matrix)
```

## Rank

The rank of a matrix is the number of linearly independent rows (or columns).

**Key insights:**
- rank(A) ≤ min(m, n) for an m×n matrix
- Full rank means maximal linear independence
- Rank-deficient matrices don't have inverses

**Application:** Checking if factor models have redundant factors.

## Practical Example: Correlation Matrix

```python
import numpy as np

# Historical returns for 3 assets
returns = np.array([
    [0.05, 0.03, 0.08, 0.02],  # Asset 1
    [0.02, 0.04, 0.06, 0.01],  # Asset 2
    [0.03, 0.05, 0.07, 0.04]   # Asset 3
])

# Calculate covariance matrix
cov_matrix = np.cov(returns)
print("Covariance Matrix:")
print(cov_matrix)

# Calculate correlation matrix
correlation_matrix = np.corrcoef(returns)
print("\nCorrelation Matrix:")
print(correlation_matrix)

# Properties of correlation matrix:
# 1. Symmetric
print(f"\nSymmetric: {np.allclose(correlation_matrix, correlation_matrix.T)}")

# 2. Diagonal elements are 1
print(f"Diagonal: {np.diag(correlation_matrix)}")

# 3. Elements between -1 and 1
print(f"Range: [{correlation_matrix.min():.2f}, {correlation_matrix.max():.2f}]")
```

## Key Takeaways

1. **Matrix multiplication is composition**: Combining transformations, calculating portfolio metrics
2. **Covariance matrices are symmetric**: Σ = Σᵀ, appears everywhere in finance
3. **Inverse solves equations**: Ax = b ⟹ x = A⁻¹b
4. **Determinant tests invertibility**: det(A) = 0 means singular
5. **Trace = sum of eigenvalues**: Total variance, total risk

## Next Steps

Now that you understand matrices, you're ready to explore:
- Linear transformations (geometric interpretation of matrices)
- Eigenvalues and eigenvectors (special directions preserved by transformations)
- Matrix decompositions (factoring matrices into simpler components)
