"""
Manually inspect Deep Learning book pages to find chapter boundaries
"""

import fitz
from pathlib import Path


def inspect_pages():
    pdf_path = "../content/machine_learning/deep_learning_foundations_and_concepts.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print("=" * 80)
    print("Deep Learning Book - Page Content Inspection")
    print("=" * 80)
    print(f"Total pages: {total_pages}\n")

    # Inspect key pages to understand structure
    pages_to_inspect = [
        1, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100,
        120, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500
    ]

    for page_num in pages_to_inspect:
        if page_num >= total_pages:
            continue

        page = doc[page_num]
        text = page.get_text()

        print(f"\n{'=' * 80}")
        print(f"PAGE {page_num + 1}")
        print('=' * 80)

        # Show first 500 characters
        preview = text[:800].strip()
        print(preview)

        if len(text) > 800:
            print("\n[... content continues ...]")

        print()

    doc.close()

    print("\n" + "=" * 80)
    print("INSTRUCTIONS")
    print("=" * 80)
    print("\nLook through the output above and identify:")
    print("1. Where does the main content start (after preface, TOC)?")
    print("2. What are the chapter titles?")
    print("3. On which pages do new chapters begin?")
    print("\nLook for patterns like:")
    print("  - Large section titles")
    print("  - Page headers/footers with chapter names")
    print("  - Numbered sections (1.1, 2.1, etc.)")
    print("  - Sudden topic changes")


if __name__ == "__main__":
    inspect_pages()
