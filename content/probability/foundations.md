---
title: Probability Foundations
category: probability
subcategory: foundations
difficulty: 1
---

# Probability Foundations

Understanding the fundamental concepts of probability theory: sample spaces, events, axioms, and basic rules that form the foundation for all probabilistic reasoning.

## Sample Spaces and Events

### Sample Space (Ω)

The set of all possible outcomes of a random experiment.

**Examples**:
- Coin flip: Ω = {H, T}
- Die roll: Ω = {1, 2, 3, 4, 5, 6}
- Stock price tomorrow: Ω = (0, ∞)

### Events

An event is a subset of the sample space.

**Examples**:
- Rolling an even number: E = {2, 4, 6}
- Stock price increases: E = {ω ∈ Ω : S_tomorrow > S_today}

### Event Operations

- **Union** (A ∪ B): A or B occurs
- **Intersection** (A ∩ B): Both A and B occur
- **Complement** (A^c): A does not occur
- **Mutually Exclusive**: A ∩ B = ∅

## Kolmogorov's Axioms

Three axioms define a valid probability measure P:

1. **Non-negativity**: P(A) ≥ 0 for all events A
2. **Normalization**: P(Ω) = 1
3. **Additivity**: If A₁, A₂, ... are mutually exclusive, then
   ```
   P(⋃ᵢ Aᵢ) = Σᵢ P(Aᵢ)
   ```

## Basic Probability Rules

### Complement Rule

```
P(A^c) = 1 - P(A)
```

### Addition Rule

For any events A and B:
```
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
```

If mutually exclusive (A ∩ B = ∅):
```
P(A ∪ B) = P(A) + P(B)
```

### Multiplication Rule

For independent events:
```
P(A ∩ B) = P(A)·P(B)
```

For dependent events:
```
P(A ∩ B) = P(A)·P(B|A) = P(B)·P(A|B)
```

## Conditional Probability

The probability of A given that B has occurred:

```
P(A|B) = P(A ∩ B) / P(B)    if P(B) > 0
```

**Interpretation**: Restricts the sample space to B.

### Law of Total Probability

If B₁, B₂, ..., Bₙ partition the sample space:
```
P(A) = Σᵢ P(A|Bᵢ)·P(Bᵢ)
```

### Bayes' Theorem

Update prior beliefs with evidence:
```
P(B|A) = P(A|B)·P(B) / P(A)
       = P(A|B)·P(B) / [Σᵢ P(A|Bᵢ)·P(Bᵢ)]
```

**Components**:
- P(B): Prior probability
- P(A|B): Likelihood
- P(B|A): Posterior probability

## Independence

Events A and B are independent if:
```
P(A ∩ B) = P(A)·P(B)
```

Equivalently:
```
P(A|B) = P(A)
P(B|A) = P(B)
```

**Note**: Independence ≠ Mutually exclusive (opposite concepts)

## Counting Methods

### Multiplication Principle

If there are n₁ ways for event 1 and n₂ ways for event 2:
```
Total ways = n₁ × n₂
```

### Permutations

Ordered arrangements of n objects taken r at a time:
```
P(n, r) = n!/(n-r)!
```

### Combinations

Unordered selections of r objects from n:
```
C(n, r) = n!/(r!(n-r)!)
```

## Financial Examples

### Credit Default

Probability that a bond defaults:
```
P(Default) = 0.05
P(No Default) = 0.95
```

### Portfolio Diversification

If two assets are independent:
```
P(Both decline) = P(A declines)·P(B declines)
```

### Conditional Risk

Probability of stock decline given recession:
```
P(Decline|Recession) = P(Decline ∩ Recession) / P(Recession)
```

### Bayesian Credit Scoring

Update default probability given payment history:
```
P(Default|Late Payment) = P(Late|Default)·P(Default) / P(Late)
```

## Practice Problems

1. A portfolio has P(Profit) = 0.6. What is P(Loss)?

2. Two stocks: P(A up) = 0.7, P(B up) = 0.6, P(Both up) = 0.4
   Are they independent?

3. Disease prevalence: 1%. Test: 95% sensitivity, 98% specificity.
   If tested positive, what's probability of having disease?

4. A die is rolled. Given the result is even, what's the probability it's greater than 3?

## Common Pitfalls

- **Prosecutor's Fallacy**: Confusing P(A|B) with P(B|A)
- **Base Rate Neglect**: Ignoring prior probabilities
- **Independence Assumption**: Assuming independence when not true
- **Double Counting**: In addition rule, don't forget to subtract intersection

## Next Steps

- **Random Variables**: Functions mapping outcomes to numbers
- **Distributions**: Describing probability across values
- **Expectation**: Computing average outcomes
- **Limit Theorems**: Convergence properties
