#!/usr/bin/env python3
"""
Analyze Bouchaud book structure to identify statistics and time series chapters
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz  # PyMuPDF
import re

def extract_toc(pdf_path):
    """Extract table of contents and chapter information"""
    print("=" * 80)
    print("Analyzing Bouchaud Book Structure")
    print("=" * 80)
    print()

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    print()

    # Look at first 30 pages for TOC
    print("Scanning first 30 pages for Table of Contents...")
    print()

    toc_text = ""
    for i in range(min(30, total_pages)):
        page = doc[i]
        text = page.get_text()
        toc_text += text + "\n"

        # Try to find chapter/section patterns
        print("=" * 80)
        print("TABLE OF CONTENTS / CHAPTERS")
        print("=" * 80)

        # Look for common patterns
        chapter_patterns = [
            r'Chapter\s+(\d+)[:\.\s]+(.+?)(?=\n|\d+$)',
            r'CHAPTER\s+(\d+)[:\.\s]+(.+?)(?=\n|\d+$)',
            r'^(\d+)\.\s+(.+?)(?=\n|\d+$)',
            r'Part\s+([IVX]+)[:\.\s]+(.+?)(?=\n)',
            r'PART\s+([IVX]+)[:\.\s]+(.+?)(?=\n)',
        ]

        chapters_found = []
        for pattern in chapter_patterns:
            matches = re.finditer(pattern, toc_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                chapters_found.append((match.group(1), match.group(2).strip()))

        if chapters_found:
            print("\nChapters/Sections found:")
            for num, title in chapters_found:
                print(f"  {num}. {title}")
        else:
            print("\nNo clear chapter structure found in standard format.")
            print("Showing first 2000 characters of TOC area:")
            print("-" * 80)
            print(toc_text[:2000])

        print()
        print("=" * 80)
        print("SEARCHING FOR STATISTICS & TIME SERIES KEYWORDS")
        print("=" * 80)

        # Search entire book for relevant keywords
        keywords = [
            'time series', 'time-series', 'autocorrelation', 'ARMA', 'GARCH',
            'stochastic process', 'random walk', 'brownian motion',
            'variance', 'volatility', 'distribution', 'gaussian', 'heavy tail',
            'tail risk', 'extreme value', 'correlation', 'covariance',
            'statistical', 'probability distribution', 'moment',
            'kurtosis', 'skewness', 'fat tail'
        ]

        keyword_pages = {kw: [] for kw in keywords}

        print(f"\nScanning all {total_pages} pages for keywords...")
        for page_num in range(total_pages):
            text = doc[page_num].get_text().lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    keyword_pages[keyword].append(page_num + 1)

        # Show results
        print("\nKeyword frequency (pages where found):")
        for keyword, pages in sorted(keyword_pages.items(), key=lambda x: len(x[1]), reverse=True):
            if pages:
                page_ranges = []
                if len(pages) <= 10:
                    page_ranges = str(pages[:10])
                else:
                    page_ranges = f"{pages[0]}-{pages[-1]} ({len(pages)} occurrences)"
                print(f"  '{keyword}': {page_ranges}")

        print()
        print("=" * 80)
        print("SAMPLE CONTENT FROM KEY PAGES")
        print("=" * 80)

        # Show sample from pages with most time series content
        time_series_pages = keyword_pages.get('time series', []) or keyword_pages.get('time-series', [])
        if time_series_pages:
            sample_page = time_series_pages[len(time_series_pages)//2]  # Middle page
            print(f"\nSample from page {sample_page} (time series content):")
            print("-" * 80)
            sample_text = doc[sample_page - 1].get_text()
            print(sample_text[:1500])

        print()
        print("=" * 80)
        print("Analysis complete!")
        print("=" * 80)

    doc.close()

if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    extract_toc(pdf_path)
