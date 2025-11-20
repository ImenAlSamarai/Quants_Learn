#!/usr/bin/env python3
"""
Extract heavy-tailed distributions content from Bouchaud Chapter 1
Sections: 1.5 (Diverging moments), 1.8 (Lévy distributions), 1.9 (Other distributions)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz

def extract_chapter1_sections(pdf_path):
    """Extract specific sections from Chapter 1"""
    print("=" * 80)
    print("Extracting Heavy-Tailed Distributions Content from Bouchaud Ch 1")
    print("=" * 80)
    print()

    doc = fitz.open(pdf_path)

    # Chapter 1 starts around page 17 based on TOC analysis
    # We need sections 1.5, 1.8, 1.9

    print("Searching for Section 1.5: Divergence of moments...")
    print()

    # Scan pages 17-40 for Chapter 1 content
    chapter1_text = ""
    section_markers = []

    for page_num in range(16, min(50, len(doc))):  # Start from page 17 (index 16)
        page = doc[page_num]
        text = page.get_text()

        # Check if this page contains section markers
        if "1.5" in text and "moment" in text.lower():
            section_markers.append(("1.5", page_num + 1))
            print(f"✓ Found Section 1.5 on page {page_num + 1}")
        if "1.6" in text and "gaussian" in text.lower():
            section_markers.append(("1.6", page_num + 1))
            print(f"✓ Found Section 1.6 on page {page_num + 1}")
        if "1.7" in text and "log-normal" in text.lower():
            section_markers.append(("1.7", page_num + 1))
            print(f"✓ Found Section 1.7 on page {page_num + 1}")
        if "1.8" in text and ("l´evy" in text.lower() or "levy" in text.lower()):
            section_markers.append(("1.8", page_num + 1))
            print(f"✓ Found Section 1.8 on page {page_num + 1}")
        if "1.9" in text and "other distributions" in text.lower():
            section_markers.append(("1.9", page_num + 1))
            print(f"✓ Found Section 1.9 on page {page_num + 1}")
        if "1.10" in text and "summary" in text.lower():
            section_markers.append(("1.10", page_num + 1))
            print(f"✓ Found Section 1.10 on page {page_num + 1}")

    print()
    print("=" * 80)
    print("Section Markers Found:")
    print("=" * 80)
    for section, page in section_markers:
        print(f"  Section {section}: Page {page}")

    print()
    print("=" * 80)
    print("Extracting Section 1.5: Divergence of Moments")
    print("=" * 80)

    # Find section 1.5 and extract until 1.6
    section_15_start = None
    section_16_start = None

    for section, page in section_markers:
        if section == "1.5":
            section_15_start = page - 1  # Convert to 0-indexed
        if section == "1.6":
            section_16_start = page - 1

    if section_15_start is not None:
        # Extract 1.5 content
        end_page = section_16_start if section_16_start else section_15_start + 3
        section_15_text = ""
        for page_num in range(section_15_start, min(end_page, len(doc))):
            section_15_text += doc[page_num].get_text()

        print(f"\nExtracted {len(section_15_text)} characters from Section 1.5")
        print("\nFirst 1500 characters:")
        print("-" * 80)
        print(section_15_text[:1500])

    print()
    print("=" * 80)
    print("Extracting Section 1.8: Lévy Distributions and Paretian Tails")
    print("=" * 80)

    # Find section 1.8 and extract until 1.9
    section_18_start = None
    section_19_start = None

    for section, page in section_markers:
        if section == "1.8":
            section_18_start = page - 1
        if section == "1.9":
            section_19_start = page - 1

    if section_18_start is not None:
        # Extract 1.8 content
        end_page = section_19_start if section_19_start else section_18_start + 5
        section_18_text = ""
        for page_num in range(section_18_start, min(end_page, len(doc))):
            section_18_text += doc[page_num].get_text()

        print(f"\nExtracted {len(section_18_text)} characters from Section 1.8")
        print("\nFirst 2000 characters:")
        print("-" * 80)
        print(section_18_text[:2000])

    print()
    print("=" * 80)
    print("Extracting Section 1.9: Other Distributions")
    print("=" * 80)

    # Find section 1.9 and extract until 1.10
    section_110_start = None

    for section, page in section_markers:
        if section == "1.10":
            section_110_start = page - 1

    if section_19_start is not None:
        # Extract 1.9 content
        end_page = section_110_start if section_110_start else section_19_start + 4
        section_19_text = ""
        for page_num in range(section_19_start, min(end_page, len(doc))):
            section_19_text += doc[page_num].get_text()

        print(f"\nExtracted {len(section_19_text)} characters from Section 1.9")
        print("\nFirst 1500 characters:")
        print("-" * 80)
        print(section_19_text[:1500])

    # Save extracted content for later use
    output = {
        "section_15": section_15_text if section_15_start else "",
        "section_18": section_18_text if section_18_start else "",
        "section_19": section_19_text if section_19_start else ""
    }

    print()
    print("=" * 80)
    print("Summary of Extracted Content")
    print("=" * 80)
    print(f"Section 1.5 (Diverging Moments): {len(output['section_15'])} chars")
    print(f"Section 1.8 (Lévy Distributions): {len(output['section_18'])} chars")
    print(f"Section 1.9 (Other Distributions): {len(output['section_19'])} chars")
    print(f"\nTotal content: {sum(len(v) for v in output.values())} characters")

    doc.close()

    return output

if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    extract_chapter1_sections(pdf_path)
