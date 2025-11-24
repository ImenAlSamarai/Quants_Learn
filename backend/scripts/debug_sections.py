"""
Debug: What sections actually exist in Chapter 3?

This helps us understand why section extraction is failing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_extractor import ESLBookExtractor
import re

def find_sections():
    pdf_path = "../content/machine_learning/elements_of_statistical_learning.pdf"

    print("="*80)
    print("Chapter 3 Section Analysis")
    print("="*80)
    print()

    extractor = ESLBookExtractor(pdf_path)
    chapter = extractor.extract_chapter(3)

    if not chapter:
        print("Failed to extract chapter!")
        return

    text = chapter['text']
    lines = text.split('\n')

    # Find all section headings
    section_pattern = r'^(3\.\d+(?:\.\d+)?)\s+(.+)$'

    print("Sections found in Chapter 3:")
    print("-"*80)

    sections_found = []
    for i, line in enumerate(lines):
        match = re.match(section_pattern, line.strip())
        if match:
            section_num = match.group(1)
            title = match.group(2).strip()
            sections_found.append((section_num, title))
            print(f"  {section_num:10s} {title}")

    print()
    print(f"Total sections found: {len(sections_found)}")
    print()

    # Check specific sections we're trying to index
    print("="*80)
    print("Checking sections needed for our 4 topics:")
    print("="*80)
    print()

    needed_sections = {
        "Linear Regression": ["3.2", "3.2.1", "3.2.2", "3.2.3"],
        "Subset Selection": ["3.3", "3.3.1", "3.3.2", "3.3.3"],
        "Ridge Regression": ["3.4.1", "3.4.2"],
        "Lasso Regression": ["3.4.2", "3.4.3", "3.4.4"]
    }

    found_nums = [s[0] for s in sections_found]

    for topic, sections in needed_sections.items():
        print(f"\n{topic}:")
        for sec in sections:
            if sec in found_nums:
                print(f"  ✓ {sec} found")
            else:
                print(f"  ✗ {sec} NOT FOUND")

    print()
    print("="*80)
    print("Analysis:")
    print("="*80)

    # Look for section 3.4 structure
    print("\nSection 3.4 subsections found:")
    section_3_4 = [s for s in sections_found if s[0].startswith('3.4')]
    for num, title in section_3_4:
        print(f"  {num}: {title}")

    # Alternative: just extract entire section 3.4 content
    print("\n" + "="*80)
    print("Alternative: Extract full section text instead of subsections")
    print("="*80)
    print()

    # Find where section 3.4 starts
    section_3_4_start = None
    section_3_4_end = None

    for i, line in enumerate(lines):
        if re.match(r'^3\.4\s+', line.strip()):
            section_3_4_start = i
        elif section_3_4_start and re.match(r'^3\.5\s+', line.strip()):
            section_3_4_end = i
            break

    if section_3_4_start:
        if not section_3_4_end:
            section_3_4_end = len(lines)

        section_3_4_text = '\n'.join(lines[section_3_4_start:section_3_4_end])
        print(f"Section 3.4 found: lines {section_3_4_start} to {section_3_4_end}")
        print(f"Content length: {len(section_3_4_text)} characters")
        print()
        print("First 500 characters:")
        print("-"*80)
        print(section_3_4_text[:500])
    else:
        print("Section 3.4 not found!")

    extractor.close()


if __name__ == "__main__":
    find_sections()
