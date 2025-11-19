#!/usr/bin/env python3
"""
Quick script to analyze the Elements of Statistical Learning PDF
Extract TOC and chapter structure
"""

import fitz  # PyMuPDF
import re

def extract_toc(pdf_path, max_pages=30):
    """Extract table of contents from first pages"""
    doc = fitz.open(pdf_path)

    print(f"Total pages: {len(doc)}")
    print(f"Analyzing first {max_pages} pages for TOC...\n")
    print("="*80)

    toc_text = ""
    for page_num in range(min(max_pages, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        toc_text += f"\n--- Page {page_num + 1} ---\n{text}\n"

    doc.close()
    return toc_text

def parse_chapters(toc_text):
    """Parse chapter structure from TOC text"""
    # Look for chapter patterns like "1. Introduction" or "Chapter 1"
    chapter_pattern = r'^\s*(\d+)\s+([A-Z][A-Za-z\s]+)\s+(\d+)\s*$'

    lines = toc_text.split('\n')
    chapters = []

    for line in lines:
        # Match numbered chapters
        match = re.match(r'^\s*(\d+)\.\s+([A-Z].*?)\s+\.?\s*(\d+)\s*$', line)
        if match:
            chapters.append({
                'number': match.group(1),
                'title': match.group(2).strip(),
                'page': match.group(3)
            })

    return chapters

if __name__ == "__main__":
    pdf_path = "content/machine_learning/elements_of_statistical_learning.pdf"

    print("Elements of Statistical Learning - Structure Analysis")
    print("="*80)

    # Extract TOC
    toc_text = extract_toc(pdf_path)

    # Save to file for review
    with open('/tmp/esl_toc.txt', 'w') as f:
        f.write(toc_text)

    print("\nTOC extracted and saved to /tmp/esl_toc.txt")
    print("\nSearching for chapter structure...")

    # Parse chapters
    chapters = parse_chapters(toc_text)

    if chapters:
        print(f"\nFound {len(chapters)} chapters:")
        print("-"*80)
        for ch in chapters:
            print(f"Chapter {ch['number']}: {ch['title']} (Page {ch['page']})")
    else:
        print("\nChapter structure not found in standard format.")
        print("Printing first 3000 characters of TOC:")
        print("-"*80)
        print(toc_text[:3000])
