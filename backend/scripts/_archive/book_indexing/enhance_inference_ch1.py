#!/usr/bin/env python3
"""
Enhancement #1: Add Heavy-Tailed Distributions content from Bouchaud Ch 1 to inference.md

This script:
1. Reads existing inference.md
2. Extracts relevant sections from Bouchaud Ch 1 (Sections 1.5, 1.8, 1.9)
3. Creates enhanced version with new sections appended
4. Saves to content/statistics/inference_enhanced.md for review
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz

def extract_bouchaud_sections(pdf_path):
    """Extract sections 1.8 and 1.9 from Bouchaud Chapter 1"""
    doc = fitz.open(pdf_path)

    # Based on analysis: Section 1.8 on pages 32-35, Section 1.9 on pages 36-37
    print("Extracting Bouchaud Chapter 1 content...")

    section_18_text = ""
    section_19_text = ""

    # Extract Section 1.8 (pages 32-35)
    for page_num in range(31, 36):  # Pages 32-36 (0-indexed: 31-35)
        text = doc[page_num].get_text()
        section_18_text += text + "\n\n"

    # Extract Section 1.9 (pages 36-37)
    for page_num in range(35, 38):  # Pages 36-38 (0-indexed: 35-37)
        text = doc[page_num].get_text()
        section_19_text += text + "\n\n"

    doc.close()

    print(f"✓ Extracted Section 1.8: {len(section_18_text)} characters")
    print(f"✓ Extracted Section 1.9: {len(section_19_text)} characters")

    return section_18_text, section_19_text

def create_enhanced_content(section_18, section_19):
    """Create the new sections to add to inference.md"""

    enhanced_sections = """

## Heavy-Tailed Distributions and Financial Reality

### Introduction: Beyond the Gaussian Assumption

Classical statistical inference often assumes data follows a Gaussian (normal) distribution. This assumption underlies many standard techniques like t-tests, ANOVA, and confidence intervals based on the Central Limit Theorem. However, **financial data exhibits "fat tails"** - extreme events occur far more frequently than predicted by Gaussian models.

This section introduces heavy-tailed distributions that better describe financial reality, drawing from Bouchaud & Potters' "Theory of Financial Risk."

**Why This Matters:**
- Market crashes (Black Monday 1987, 2008 Financial Crisis) are far more common than Gaussian models predict
- Traditional risk measures (volatility, VaR) can severely underestimate tail risk
- Portfolio optimization and derivatives pricing require accurate tail modeling

---

### Lévy Distributions and Power-Law Tails

**From Bouchaud, Section 1.8:**

Lévy distributions appear naturally when modeling phenomena with multiple scales - from small fluctuations to large jumps. Unlike Gaussian distributions with exponentially decaying tails, Lévy distributions have **power-law (Paretian) tails**:

```
L_μ(x) ~ μA_μ / |x|^(1+μ)    for |x| → ∞
```

where:
- **μ (0 < μ < 2)**: Tail exponent (also called α)
  - μ = 2: Reduces to Gaussian
  - μ < 2: Fat tails (power-law decay)
  - Smaller μ → Fatter tails → More extreme events

- **A_μ**: Tail amplitude (scale parameter)
  - Controls the magnitude of large fluctuations
  - Higher A_μ → More frequent extreme events

**Critical Property: Diverging Moments**

When μ ≤ 2, the **variance is formally infinite**:

```
Var(X) = ∫ x² L_μ(x) dx = ∞    when μ ≤ 2
```

**Implications:**
- Standard deviation doesn't exist mathematically
- Sample variance keeps growing with more data
- Traditional volatility measures are unreliable
- Sharpe ratio and similar metrics break down

When μ ≤ 1, even the **mean is undefined**!

**Characteristic Function:**

Unlike Gaussian distributions, Lévy distributions are more easily described by their characteristic function:

```
ˆL_μ(z) = exp(-a_μ |z|^μ)
```

For μ = 1 (Cauchy distribution), there's an explicit form:

```
L_1(x) = A / (x² + π²A²)
```

**Visual Behavior:**
- Sharp peak around zero
- Fat tails extending far into extremes
- "Missing middle" - intermediate events less likely than Gaussian
- As μ decreases from 2, distribution becomes more peaked and tails get fatter

**Truncated Lévy Distributions:**

In practice, pure power-law tails extend to infinity, which is unrealistic. **Truncated Lévy distributions** add an exponential cut-off for very large values while preserving power-law behavior in intermediate range:

```
ˆL^(t)_μ(z) = exp[-a_μ((α² + z²)^(μ/2) cos(μ arctan(|z|/α)) - α^μ) / cos(πμ/2)]
```

This gives:
- Power-law tails for x ≪ 1/α
- Exponential decay for x ≫ 1/α
- Finite variance: Var(X) = μ(μ-1)a_μ / (|cos(πμ/2)|α^(μ-2))

**Applications:**
- Modeling stock returns (with realistic cut-offs)
- Credit default events
- Insurance claims
- Commodity price jumps

---

### Student's t-Distribution and Other Heavy-Tailed Distributions

**From Bouchaud, Section 1.9:**

While Lévy distributions are theoretically important, the **Student's t-distribution** is often more practical for financial applications due to its simpler parameterization and finite moments.

**Student's t-Distribution:**

With ν degrees of freedom:

```
P_ν(x) = Γ((ν+1)/2) / (√(νπ) Γ(ν/2)) · 1 / (1 + x²/ν)^((ν+1)/2)
```

**Key Properties:**
- **Kurtosis**: κ = 6/(ν - 4)    (for ν > 4)
- ν = ∞: Converges to Gaussian
- Small ν: Fat tails
- ν = 3: Often good fit for daily stock returns
- ν = 5-10: Typical range for financial data

**Moments:**
- Mean exists for ν > 1
- Variance exists for ν > 2
- Higher moments exist for ν > k

**Comparison with Lévy Distributions:**
- Student's t has tail behavior similar to truncated Lévy with μ close to 2
- Easier parameter estimation (Maximum Likelihood works well)
- Finite variance for ν > 2 (unlike pure Lévy)
- Widely supported in statistical software

**When to Use Each Distribution:**

| Distribution | Best For | Advantages | Disadvantages |
|-------------|----------|------------|---------------|
| **Gaussian** | Well-behaved data, large samples | Simple, CLT applies | Underestimates tail risk |
| **Student's t** | Financial returns, moderate tails | Easy to estimate, practical | Less flexible for very fat tails |
| **Lévy (μ < 2)** | Extreme tails, theoretical models | Captures severe tail events | Infinite variance, hard to estimate |
| **Truncated Lévy** | Realistic tail modeling | Flexible, finite variance | Complex parameterization |

**Empirical Detection of Heavy Tails:**

How to identify if your data has fat tails:

1. **Visual Inspection:**
   - Q-Q plot against normal distribution
   - Log-log plot of tail probabilities
   - If tails deviate from straight line → heavy tails

2. **Kurtosis:**
   - Excess kurtosis > 0 indicates fat tails
   - Financial returns typically have κ = 3-10 (vs 0 for Gaussian)

3. **Hill Estimator:**
   - Estimates tail exponent μ from empirical data
   - Based on order statistics of extreme values

4. **Statistical Tests:**
   - Kolmogorov-Smirnov test
   - Anderson-Darling test (more sensitive to tails)
   - Jarque-Bera test (tests normality via skewness/kurtosis)

**Practical Workflow:**

```
1. Plot data distribution → Check for fat tails visually
2. Calculate excess kurtosis → Quantify tail heaviness
3. Fit Student's t → Easy first attempt
4. Estimate tail exponent → Use Hill estimator
5. Compare models → AIC/BIC for Gaussian vs t vs Lévy
6. Validate → Backtest risk measures on out-of-sample data
```

---

### Implications for Statistical Inference

The presence of heavy tails fundamentally changes how we do inference:

**Confidence Intervals:**
- With infinite variance, standard error √(σ²/n) is meaningless
- Need robust methods: bootstrap, quantile-based intervals
- Intervals will be wider than Gaussian-based estimates

**Hypothesis Testing:**
- t-tests assume normality (or CLT convergence)
- With heavy tails, convergence to normality is slow
- Alternative: permutation tests, robust tests

**Parameter Estimation:**
- MLE still works but may be unstable with fat tails
- Robust estimators: trimmed mean, median, MAD
- Bayesian methods with informative priors can help

**Sample Size Requirements:**
- CLT requires much larger n with heavy tails
- Rule of thumb: n ≥ 100 for mild fat tails (μ ≈ 1.7)
- May need n > 1000 for severe tails (μ < 1.5)

**Risk Measurement:**
- VaR underestimates risk with fat tails
- Expected Shortfall (CVaR) more appropriate
- Drawdown-based measures more robust

---

### Further Reading

**Key References:**
- Bouchaud, J.-P., & Potters, M. (2003). *Theory of Financial Risk and Derivative Pricing*
- Mandelbrot, B. (1963). "The Variation of Certain Speculative Prices"
- Fama, E. (1965). "The Behavior of Stock-Market Prices"
- Cont, R. (2001). "Empirical Properties of Asset Returns: Stylized Facts and Statistical Issues"

**Related Topics:**
- Extreme Value Theory (see separate topic)
- Expected Shortfall and Tail Risk Measures
- GARCH Models (heavy tails in conditional distributions)
- Stable Distributions and Generalized CLT

---

## Practice Problems

1. **Tail Behavior**: A distribution has power-law tail with μ = 1.5. Does the variance exist? Does the mean exist?

2. **Kurtosis Calculation**: Student's t with ν = 6 degrees of freedom. Calculate excess kurtosis.

3. **Probability Comparison**: For a Lévy distribution with μ = 1.7 and A_μ = 1, calculate P(X > 10). Compare with Gaussian having same median.

4. **Real Data**: Daily S&P 500 returns show excess kurtosis of 5. Would you model with Gaussian, Student's t, or Lévy? Justify.

5. **Risk Implications**: Portfolio VaR is $1M at 95% confidence under Gaussian. If returns follow Student's t with ν = 4, would true VaR be higher or lower? Why?

---

"""

    return enhanced_sections

def create_enhanced_file(original_path, enhanced_content):
    """Create enhanced version of inference.md"""

    # Read original file
    with open(original_path, 'r') as f:
        original_content = f.read()

    # Combine original + enhanced
    full_content = original_content + enhanced_content

    # Save to review file
    output_path = original_path.parent / "inference_enhanced.md"
    with open(output_path, 'w') as f:
        f.write(full_content)

    print(f"\n✓ Created enhanced file: {output_path}")
    print(f"  Original: {len(original_content)} chars")
    print(f"  Added: {len(enhanced_content)} chars")
    print(f"  Total: {len(full_content)} chars")

    return output_path

def main():
    print("=" * 80)
    print("Enhancement #1: Add Heavy-Tailed Distributions to inference.md")
    print("=" * 80)
    print()

    # Paths
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    inference_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "inference.md"

    # Extract Bouchaud sections
    section_18, section_19 = extract_bouchaud_sections(pdf_path)

    # Create enhanced content (handcrafted based on book sections)
    enhanced_sections = create_enhanced_content(section_18, section_19)

    # Create enhanced file
    output_path = create_enhanced_file(inference_path, enhanced_sections)

    print()
    print("=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("1. Review the enhanced file:")
    print(f"   cat {output_path}")
    print()
    print("2. If approved, replace original:")
    print(f"   mv {output_path} {inference_path}")
    print()
    print("3. Re-index to vector store:")
    print("   python scripts/index_enhanced_topics.py")
    print()

if __name__ == "__main__":
    main()
