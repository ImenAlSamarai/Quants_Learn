#!/usr/bin/env python3
"""
Preview extracted content from Bouchaud Ch 1 for heavy-tailed distributions
Show what will be added to inference.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz

def preview_content(pdf_path):
    """Preview content that will be added to inference.md"""
    print("=" * 80)
    print("PREVIEW: Content to Add to inference.md")
    print("Enhancement #1: Heavy-Tailed Distributions")
    print("=" * 80)
    print()

    doc = fitz.open(pdf_path)

    # Based on previous analysis, extract pages 28-37 (Chapter 1 relevant sections)
    # Section 1.5: ~page 29
    # Section 1.8: pages 32-35
    # Section 1.9: pages 36-37

    print("Extracting full Chapter 1 content (pages 28-38)...")
    print()

    chapter1_content = ""
    for page_num in range(27, 38):  # Pages 28-38 (0-indexed: 27-37)
        page = doc[page_num]
        text = page.get_text()
        chapter1_content += text + "\n\n"

    # Show summary
    print(f"Total extracted: {len(chapter1_content)} characters")
    print()

    # Show section breakdown
    print("=" * 80)
    print("SECTION 1.5: Divergence of Moments - Asymptotic Behaviour")
    print("=" * 80)
    section_15_start = chapter1_content.find("1.5")
    section_16_start = chapter1_content.find("1.6")
    if section_15_start >= 0 and section_16_start >= 0:
        section_15 = chapter1_content[section_15_start:section_16_start]
        print(f"Length: {len(section_15)} characters")
        print()
        print("Preview (first 800 chars):")
        print("-" * 80)
        print(section_15[:800])
    else:
        print("⚠️  Section 1.5 not found with markers, showing page 29 content:")
        print("-" * 80)
        print(doc[28].get_text()[:1200])

    print()
    print("=" * 80)
    print("SECTION 1.8: Lévy Distributions and Paretian Tails")
    print("=" * 80)
    section_18_start = chapter1_content.find("1.8")
    section_19_start = chapter1_content.find("1.9")
    if section_18_start >= 0 and section_19_start >= 0:
        section_18 = chapter1_content[section_18_start:section_19_start]
        print(f"Length: {len(section_18)} characters")
        print()
        print("Preview (first 1200 chars):")
        print("-" * 80)
        print(section_18[:1200])
    else:
        print("Using detected content from pages 32-35")
        section_18_pages = ""
        for page_num in range(31, 35):
            section_18_pages += doc[page_num].get_text() + "\n"
        print(f"Length: {len(section_18_pages)} characters")
        print()
        print("Preview (first 1200 chars):")
        print("-" * 80)
        print(section_18_pages[:1200])

    print()
    print("=" * 80)
    print("SECTION 1.9: Other Distributions")
    print("=" * 80)
    if section_19_start >= 0:
        section_110_start = chapter1_content.find("1.10")
        section_19 = chapter1_content[section_19_start:section_110_start if section_110_start >= 0 else section_19_start + 3000]
        print(f"Length: {len(section_19)} characters")
        print()
        print("Preview (first 1000 chars):")
        print("-" * 80)
        print(section_19[:1000])

    print()
    print("=" * 80)
    print("KEY CONCEPTS TO BE ADDED")
    print("=" * 80)
    print("""
From Section 1.5 - Divergence of Moments:
  - When moments diverge (infinite variance/kurtosis)
  - Asymptotic behavior of distributions
  - Implications for financial modeling

From Section 1.8 - Lévy Distributions:
  - Power-law tails (Pareto distributions)
  - Lévy stable distributions
  - Truncated Lévy distributions
  - Tail parameter μ and its interpretation
  - Why Gaussian assumption fails for finance

From Section 1.9 - Other Heavy-Tailed Distributions:
  - Student's t-distribution
  - Hyperbolic distributions
  - Comparison of tail behaviors
  - When to use each distribution
    """)

    print()
    print("=" * 80)
    print("PROPOSED ADDITION TO inference.md")
    print("=" * 80)
    print("""
Will add new sections at the end of inference.md:

## Heavy-Tailed Distributions and Diverging Moments

### Why Gaussian is Not Enough for Financial Data
[Introductory paragraph explaining fat tails in finance]

### Lévy Distributions and Power-Law Tails
[Content from Section 1.8]
- Mathematical definition
- Tail parameter μ
- Truncated Lévy distributions
- Applications to financial returns

### Diverging Moments
[Content from Section 1.5]
- When variance doesn't exist
- Implications for risk measurement
- Asymptotic behavior

### Other Heavy-Tailed Distributions
[Content from Section 1.9]
- Student's t-distribution
- Comparison with Lévy distributions
- Practical applications

### Empirical Detection of Heavy Tails
- How to identify fat tails in data
- Statistical tests
- Estimation methods
    """)

    doc.close()

if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    preview_content(pdf_path)
