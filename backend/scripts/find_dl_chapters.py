"""
Systematically scan Deep Learning PDF to find all chapter boundaries
"""

import fitz
import re
from pathlib import Path


def find_all_chapters():
    pdf_path = "../content/machine_learning/deep_learning_foundations_and_concepts.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print("=" * 80)
    print("Deep Learning Book - Chapter Boundary Detection")
    print("=" * 80)
    print(f"Total pages: {total_pages}\n")

    chapters = {}

    # Scan every page looking for chapter markers
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')

        # Look for patterns like "N. CHAPTER TITLE" or chapter headers
        for line in lines[:30]:  # Check first 30 lines of each page
            line = line.strip()

            # Pattern 1: "3. STANDARD DISTRIBUTIONS"
            match1 = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s:]+)$', line)

            # Pattern 2: "Chapter N" followed by title
            match2 = re.match(r'^Chapter\s+(\d+)', line, re.IGNORECASE)

            # Pattern 3: Just large section numbers at start "N.1"
            match3 = re.match(r'^(\d+)\.1\s+', line)

            if match1:
                chapter_num = int(match1.group(1))
                title = match1.group(2).strip()
                if chapter_num not in chapters or page_num < chapters[chapter_num]['page']:
                    chapters[chapter_num] = {
                        'page': page_num,
                        'title': title,
                        'pattern': 'format1'
                    }
                    print(f"Found Chapter {chapter_num}: {title} (page {page_num + 1}, pattern 1)")

            elif match2:
                chapter_num = int(match2.group(1))
                if chapter_num not in chapters or page_num < chapters[chapter_num]['page']:
                    # Try to get title from next line
                    title_line_idx = lines.index(line) + 1
                    title = lines[title_line_idx].strip() if title_line_idx < len(lines) else "Unknown"
                    chapters[chapter_num] = {
                        'page': page_num,
                        'title': title,
                        'pattern': 'format2'
                    }
                    print(f"Found Chapter {chapter_num}: {title} (page {page_num + 1}, pattern 2)")

            elif match3:
                chapter_num = int(match3.group(1))
                # Only add if we don't already have this chapter
                if chapter_num not in chapters:
                    chapters[chapter_num] = {
                        'page': page_num,
                        'title': 'Unknown',
                        'pattern': 'format3'
                    }
                    print(f"Found Chapter {chapter_num}: section 1 (page {page_num + 1}, pattern 3)")

    doc.close()

    # Print summary
    print("\n" + "=" * 80)
    print("CHAPTER MAPPING SUMMARY")
    print("=" * 80)
    print("\nUpdate dl_book_extractor.py with this mapping:\n")
    print("chapter_mapping = {")

    sorted_chapters = sorted(chapters.items())
    for i, (ch_num, ch_data) in enumerate(sorted_chapters):
        start_page = ch_data['page']

        # Find end page (start of next chapter - 1)
        if i + 1 < len(sorted_chapters):
            end_page = sorted_chapters[i + 1][1]['page'] - 1
        else:
            end_page = total_pages - 1

        title = ch_data['title']
        print(f"    {ch_num}: ({start_page}, {end_page}),  # {title}")

    print("}")

    print(f"\n\nTotal chapters found: {len(chapters)}")


if __name__ == "__main__":
    find_all_chapters()
