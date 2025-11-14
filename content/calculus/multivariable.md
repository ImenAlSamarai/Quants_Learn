---
title: Multivariable Calculus
category: calculus
subcategory: multivariable
difficulty: 3
---

# Multivariable Calculus

Multivariable calculus extends single-variable concepts to functions of multiple variables, essential for portfolio optimization, machine learning, and multivariate statistical models.

## Partial Derivatives

For a function f(x, y), partial derivatives measure the rate of change with respect to one variable while holding others constant:

```
∂f/∂x = lim(h→0) [f(x+h, y) - f(x, y)] / h
∂f/∂y = lim(h→0) [f(x, y+h) - f(x, y)] / h
```

**Example**: f(x, y) = x²y + 3xy²
- ∂f/∂x = 2xy + 3y²
- ∂f/∂y = x² + 6xy

## The Gradient

The gradient is a vector of all partial derivatives:

```
∇f = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]
```

**Properties**:
- Points in the direction of steepest ascent
- Perpendicular to level curves/surfaces
- Magnitude indicates rate of change in that direction

## Directional Derivatives

Rate of change in an arbitrary direction u:

```
D_u f = ∇f · u
```

Maximum rate of change occurs in the direction of ∇f.

## Chain Rule (Multivariate)

If z = f(x, y), x = g(t), y = h(t):

```
dz/dt = (∂f/∂x)(dx/dt) + (∂f/∂y)(dy/dt)
```

## Optimization

### Critical Points

Find where ∇f = 0:
```
∂f/∂x = 0
∂f/∂y = 0
```

### Second Derivative Test (Hessian)

The Hessian matrix contains all second partial derivatives:

```
H = [∂²f/∂x²    ∂²f/∂x∂y]
    [∂²f/∂y∂x   ∂²f/∂y²  ]
```

At critical point (a, b):
- If det(H) > 0 and ∂²f/∂x² > 0: local minimum
- If det(H) > 0 and ∂²f/∂x² < 0: local maximum
- If det(H) < 0: saddle point
- If det(H) = 0: inconclusive

### Lagrange Multipliers

For constrained optimization:
- Minimize f(x, y) subject to g(x, y) = c

Set up the Lagrangian:
```
L(x, y, λ) = f(x, y) - λ(g(x, y) - c)
```

Solve:
```
∇f = λ∇g
g(x, y) = c
```

## Multiple Integrals

### Double Integrals

Compute volume under a surface:
```
∫∫_R f(x, y) dA
```

**Iterated integrals**:
```
∫ₐᵇ ∫_c^d f(x, y) dy dx
```

**Fubini's Theorem**: Can switch order of integration if f is continuous.

### Change of Variables (Jacobian)

When transforming coordinates (x, y) → (u, v):

```
∫∫_R f(x, y) dx dy = ∫∫_S f(x(u,v), y(u,v)) |J| du dv
```

Where J is the Jacobian determinant:
```
J = |∂x/∂u  ∂x/∂v|
    |∂y/∂u  ∂y/∂v|
```

### Polar Coordinates

For circular regions:
```
x = r cos(θ), y = r sin(θ)
J = r

∫∫_R f(x, y) dx dy = ∫∫ f(r cos θ, r sin θ) r dr dθ
```

## Financial Applications

### Portfolio Optimization

Minimize variance subject to target return:
```
min w'Σw
s.t. w'μ = μ_target
     w'1 = 1
```

Using Lagrange multipliers:
```
L = w'Σw - λ₁(w'μ - μ_target) - λ₂(w'1 - 1)
```

### Gradient Descent

Optimize parameters in machine learning:
```
θ_(t+1) = θ_t - α∇L(θ_t)
```

For neural networks, compute gradients via backpropagation.

### Maximum Likelihood Estimation

Find parameters that maximize likelihood function:
```
∂L/∂θ₁ = 0
∂L/∂θ₂ = 0
...
```

### Taylor Series (Multivariate)

Approximate functions around a point (a, b):
```
f(x, y) ≈ f(a, b) + fₓ(a,b)(x-a) + f_y(a,b)(y-b)
        + 1/2[fₓₓ(x-a)² + 2fₓᵧ(x-a)(y-b) + f_yy(y-b)²]
```

Used in delta-gamma approximations for options:
```
ΔV ≈ Δ·ΔS + 1/2·Γ·(ΔS)²
```

## Vector Calculus

### Line Integrals

Work done along a curve:
```
∫_C F · dr = ∫ₐᵇ F(r(t)) · r'(t) dt
```

### Green's Theorem

Relates line integrals to double integrals:
```
∮_C (P dx + Q dy) = ∫∫_R (∂Q/∂x - ∂P/∂y) dA
```

## Practice Problems

1. Find ∇f for f(x, y) = e^(x²+y²)
2. Optimize f(x, y) = x² + y² subject to x + y = 10
3. Compute ∫∫_R (x² + y²) dA where R is the unit circle
4. Use Hessian to classify critical points of f(x, y) = x³ - 3xy + y³

## Next Steps

- **Optimization Algorithms**: Gradient descent, Newton's method, BFGS
- **Stochastic Calculus**: Ito's lemma and stochastic differential equations
- **Differential Equations**: Partial differential equations in finance
- **Numerical Methods**: Finite differences, Monte Carlo simulation
