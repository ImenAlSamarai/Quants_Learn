#!/usr/bin/env python3
"""Find exact chapter boundaries in ESL PDF"""

import fitz

pdf_path = "content/machine_learning/elements_of_statistical_learning.pdf"
doc = fitz.open(pdf_path)

print("Searching for Chapter 3, 4, and 5 boundaries...\n")

for page_num in range(40, 150):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')[:20]  # First 20 lines

    # Check if this page starts a chapter
    for i, line in enumerate(lines):
        if line.strip() in ['3', '4', '5'] and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if 'Linear Methods' in next_line or 'Basis Expansions' in next_line:
                print(f"Page {page_num} (1-indexed: {page_num + 1}):")
                print(f"  Found: '{line}' followed by '{next_line}'")
                print(f"  First 10 lines:")
                for j, l in enumerate(lines[:10]):
                    print(f"    {j}: {l}")
                print()

doc.close()
