"""
Analyze Deep Learning book structure more carefully

This script manually inspects key pages to find real chapter boundaries
"""

import fitz
from pathlib import Path
import re


def analyze_book_structure():
    pdf_path = "../content/machine_learning/deep_learning_foundations_and_concepts.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print("=" * 80)
    print("Deep Learning Book Structure Analysis")
    print("=" * 80)
    print(f"Total pages: {total_pages}\n")

    # Sample pages throughout the book to understand structure
    sample_pages = [
        0, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
        150, 200, 250, 300, 350, 400, 450, 500, 550, 600
    ]

    print("Sampling key pages to understand structure...\n")

    chapters_found = []

    for page_num in sample_pages:
        if page_num >= total_pages:
            continue

        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')

        # Look for chapter markers
        # Common patterns: "Chapter 1", "1 Introduction", etc.
        chapter_patterns = [
            r'^Chapter\s+(\d+)',
            r'^(\d+)\s+[A-Z][a-z]+',  # "1 Introduction"
            r'^CHAPTER\s+(\d+)',
        ]

        for line in lines[:20]:  # Check first 20 lines of each page
            for pattern in chapter_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    chapter_num = match.group(1)
                    # Check if this looks like a real chapter start
                    # (large font, standalone, near top of page)
                    print(f"Page {page_num + 1:4d}: Possible Chapter {chapter_num}")
                    print(f"  First line: {line.strip()[:80]}")

                    # Show a bit more context
                    context = '\n'.join(lines[:5])
                    print(f"  Context:\n{context[:200]}...")
                    print()

                    chapters_found.append((int(chapter_num), page_num))
                    break

    doc.close()

    # Remove duplicates and sort
    chapters_found = sorted(list(set(chapters_found)))

    print("\n" + "=" * 80)
    print("Summary of Detected Chapters")
    print("=" * 80)

    if chapters_found:
        print(f"\nFound {len(chapters_found)} unique chapters:\n")
        for ch_num, page_num in chapters_found:
            print(f"  Chapter {ch_num:2d}: Page {page_num + 1}")

        print("\n" + "=" * 80)
        print("Suggested Chapter Mapping")
        print("=" * 80)
        print("\nchapter_mapping = {")
        for i, (ch_num, page_num) in enumerate(chapters_found):
            if i + 1 < len(chapters_found):
                next_page = chapters_found[i + 1][1]
                print(f"    {ch_num}: ({page_num}, {next_page - 1}),  # Pages {page_num + 1}-{next_page}")
            else:
                print(f"    {ch_num}: ({page_num}, {total_pages - 1}),  # Pages {page_num + 1}-{total_pages}")
        print("}")
    else:
        print("\nNo chapters clearly detected. Manual analysis needed.")
        print("\nTry inspecting these page ranges manually:")
        print("  - Pages 1-50: Front matter, introduction")
        print("  - Pages 50-100: Likely Chapter 1")
        print("  - Pages 100-150: Likely Chapter 2")
        print("  etc.")


if __name__ == "__main__":
    analyze_book_structure()
