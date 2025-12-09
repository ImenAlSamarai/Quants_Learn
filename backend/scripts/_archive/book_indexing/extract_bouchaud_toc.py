#!/usr/bin/env python3
"""
Extract detailed table of contents from Bouchaud book
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz

def extract_detailed_toc(pdf_path):
    """Extract TOC by looking at specific pages"""
    doc = fitz.open(pdf_path)

    print("=" * 80)
    print("Extracting Bouchaud Book Table of Contents")
    print("=" * 80)
    print()

    # Check pages 5-15 for TOC (typical location)
    for page_num in range(5, min(20, len(doc))):
        page = doc[page_num]
        text = page.get_text()

        # Check if this looks like TOC
        if 'contents' in text.lower() or 'chapter' in text.lower():
            print(f"\n--- Page {page_num + 1} ---")
            print(text[:3000])
            print()

    # Also check beginning of actual content for chapter headings
    print("\n" + "=" * 80)
    print("Scanning for Chapter Headings in Content")
    print("=" * 80)

    chapters = []
    for page_num in range(10, min(400, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')

        # Look for lines that might be chapter titles (short, mostly caps, or numbered)
        for i, line in enumerate(lines[:5]):  # Check first 5 lines of each page
            line_clean = line.strip()
            # Patterns for chapter titles
            if (len(line_clean) > 10 and len(line_clean) < 100 and
                (line_clean[0].isdigit() or
                 (line_clean.isupper() and len(line_clean.split()) > 2))):
                chapters.append((page_num + 1, line_clean))

    # Show unique chapters
    print("\nPotential Chapter Headings Found:")
    seen = set()
    for page, title in chapters:
        if title not in seen and len(title) > 15:
            print(f"  Page {page}: {title}")
            seen.add(title)
            if len(seen) >= 30:  # Limit output
                break

    doc.close()

if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    extract_detailed_toc(pdf_path)
