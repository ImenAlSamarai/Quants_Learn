---
title: Linear Algebra
category: linear_algebra
difficulty: 2
estimated_time: 30
---

# Linear Algebra: The Foundation of Quantitative Finance

Linear algebra is the mathematical framework that underlies most quantitative finance applications. From portfolio optimization to machine learning models, understanding vectors, matrices, and linear transformations is essential for any aspiring quant researcher.

## Why Linear Algebra Matters in Finance

### Portfolio Optimization
Modern Portfolio Theory (MPT) relies heavily on linear algebra. The expected returns and covariance matrix of assets form the core of mean-variance optimization:

- **Returns vector**: E[R] representing expected returns of assets
- **Covariance matrix**: Σ capturing relationships between asset returns
- **Weight vector**: w representing portfolio allocations

The optimal portfolio is found by solving: min w^T Σ w subject to constraints.

### Risk Management
Value at Risk (VaR) and other risk metrics use covariance matrices to quantify portfolio risk. Principal Component Analysis (PCA), built on eigenvalue decomposition, identifies the main risk factors driving portfolio variance.

### Factor Models
Multi-factor models like Fama-French express returns as linear combinations of factors:
R = α + β₁F₁ + β₂F₂ + ... + βₙFₙ + ε

This is fundamentally a matrix equation: R = α + Bᵀf + ε

### Machine Learning
- Support Vector Machines use hyperplanes (linear algebra concepts)
- Neural networks are compositions of matrix multiplications and nonlinear activations
- Dimensionality reduction techniques (PCA, t-SNE) rely on eigenvalues and singular values

## Core Topics

### 1. Vectors and Vector Spaces
Understanding the fundamental building blocks: what vectors represent, operations on vectors, and the concept of vector spaces.

**Key Applications:**
- Asset returns as vectors
- Portfolio weights
- Factor loadings

### 2. Matrices and Operations
Matrix multiplication, inverses, transposes, and their properties form the computational backbone of quantitative finance.

**Key Applications:**
- Covariance matrices
- Transition matrices in Markov chains
- System of linear equations

### 3. Linear Transformations
How matrices represent transformations and the geometric intuition behind them.

**Key Applications:**
- Change of basis in factor models
- Rotation and scaling in data analysis

### 4. Eigenvalues and Eigenvectors
Special vectors that remain in the same direction under transformation, revealing the intrinsic properties of matrices.

**Key Applications:**
- PCA for dimensionality reduction
- Stability analysis of systems
- Google's PageRank algorithm

### 5. Advanced Decompositions
Breaking matrices into simpler components: SVD, QR, Cholesky decomposition.

**Key Applications:**
- Risk factor decomposition
- Matrix completion in data
- Efficient numerical algorithms

## Learning Path

Start with vectors and basic operations, then progress to matrices and their properties. Once comfortable with matrix operations, study eigenvalues and eigenvectors. Finally, explore advanced decomposition techniques that power modern quantitative methods.

Each topic builds on the previous ones, creating a solid foundation for machine learning, optimization, and quantitative modeling.

## Prerequisites
- Basic calculus
- Comfort with mathematical notation
- Basic programming (Python recommended)

## Estimated Time
- Fundamentals (Vectors, Matrices): 2-3 weeks
- Intermediate (Transformations, Eigenvalues): 3-4 weeks
- Advanced (Decompositions, Applications): 2-3 weeks

Total: ~8-10 weeks with consistent practice
