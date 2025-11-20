"""
Scan specific page ranges to identify chapter boundaries
Based on patterns observed in initial inspection
"""

import fitz
import re
from pathlib import Path


def scan_page_range(doc, start, end, label):
    """Scan a range of pages looking for chapter start"""
    print(f"\n{'=' * 80}")
    print(f"Scanning pages {start}-{end} ({label})")
    print('=' * 80)

    for page_num in range(start, min(end, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')

        # Check if this looks like a chapter start
        first_100_chars = text[:200].strip()

        # Look for numbered sections or chapter titles
        for i, line in enumerate(lines[:20]):
            line = line.strip()

            # Pattern: "N. CHAPTER TITLE" in all caps
            if re.match(r'^\d+\.\s+[A-Z][A-Z\s]+$', line) and len(line) > 10:
                print(f"\n  Page {page_num + 1}: Possible chapter start")
                print(f"    Title: {line}")
                print(f"    First few lines:")
                for j in range(min(5, len(lines))):
                    if lines[j].strip():
                        print(f"      {lines[j]}")
                break

            # Pattern: Section N.1 (indicates chapter N starts here or nearby)
            section_match = re.match(r'^(\d+)\.1\s+([A-Za-z].+)$', line)
            if section_match and int(section_match.group(1)) <= 20:
                ch_num = section_match.group(1)
                section_title = section_match.group(2)
                print(f"\n  Page {page_num + 1}: Section {ch_num}.1 found")
                print(f"    Section: {line}")
                print(f"    (Chapter {ch_num} likely starts here or slightly before)")
                break


def main():
    pdf_path = "../content/machine_learning/deep_learning_foundations_and_concepts.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found")
        return

    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")

    # Based on initial inspection, scan key ranges
    ranges = [
        (20, 30, "Chapter 1 area"),
        (45, 55, "Chapter 2 area"),
        (85, 95, "Chapter 3 area"),
        (135, 145, "Chapter 4 area"),
        (155, 165, "Chapter 5 area"),
        (185, 195, "Chapter 6 area"),
        (215, 235, "Chapter 7/8 area"),
        (245, 255, "Chapter 8/9 area"),
        (295, 305, "Chapter 9/10 area"),
        (335, 355, "Chapter 11/12 area"),
        (395, 405, "Chapter 12/13 area"),
        (440, 455, "Chapter 14 area"),
        (495, 505, "Chapter 15 area"),
    ]

    for start, end, label in ranges:
        scan_page_range(doc, start, end, label)

    doc.close()


if __name__ == "__main__":
    main()
