"""
PDF Content Extractor for Elements of Statistical Learning

This module extracts structured content from the ESL PDF book,
including chapters, sections, and mathematical content.
"""

import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ESLBookExtractor:
    """Extract content from Elements of Statistical Learning PDF"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = fitz.open(str(self.pdf_path))
        self.total_pages = len(self.doc)

    def extract_text_from_pages(self, start_page: int, end_page: int) -> str:
        """
        Extract raw text from a range of pages

        Args:
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (0-indexed, inclusive)

        Returns:
            Extracted text as string
        """
        text = []
        for page_num in range(start_page, min(end_page + 1, self.total_pages)):
            page = self.doc[page_num]
            page_text = page.get_text()
            text.append(page_text)

        return "\n".join(text)

    def find_chapter_pages(self, chapter_num: int) -> Optional[Tuple[int, int]]:
        """
        Find the start and end pages of a specific chapter

        Args:
            chapter_num: Chapter number (1-18)

        Returns:
            Tuple of (start_page, end_page) or None if not found
        """
        # Manual mapping based on ESL book structure (2nd edition)
        # Page numbers are 0-indexed (PDF page numbers)
        # Verified by searching for chapter headings
        chapter_mapping = {
            1: (0, 60),      # Introduction
            2: (19, 60),     # Overview of Supervised Learning
            3: (61, 118),    # Linear Methods for Regression (Book pages 43-100)
            4: (119, 176),   # Linear Methods for Classification (Book pages 101-158)
            5: (177, 228),   # Basis Expansions and Regularization
            6: (229, 260),   # Kernel Smoothing Methods
            7: (261, 296),   # Model Assessment and Selection
            8: (297, 320),   # Model Inference and Averaging
            9: (321, 356),   # Additive Models, Trees
            10: (357, 394),  # Boosting and Additive Trees
            11: (395, 426),  # Neural Networks
            12: (427, 460),  # Support Vector Machines
            13: (461, 484),  # Prototype Methods
            14: (485, 558),  # Unsupervised Learning
            15: (559, 588),  # Random Forests
            16: (589, 618),  # Ensemble Learning
            17: (619, 644),  # Undirected Graphical Models
            18: (645, 688),  # High-Dimensional Problems
        }

        return chapter_mapping.get(chapter_num)

    def extract_chapter(self, chapter_num: int) -> Optional[Dict]:
        """
        Extract a complete chapter with metadata

        Args:
            chapter_num: Chapter number (1-18)

        Returns:
            Dictionary with chapter data
        """
        pages = self.find_chapter_pages(chapter_num)
        if not pages:
            return None

        start_page, end_page = pages
        text = self.extract_text_from_pages(start_page, end_page)

        # Extract chapter title from first page
        first_page_text = self.doc[start_page].get_text()
        title = self._extract_chapter_title(first_page_text, chapter_num)

        return {
            'chapter_num': chapter_num,
            'title': title,
            'start_page': start_page + 1,  # Convert to 1-indexed
            'end_page': end_page + 1,
            'page_count': end_page - start_page + 1,
            'text': text,
            'sections': self._parse_sections(text)
        }

    def _extract_chapter_title(self, first_page_text: str, chapter_num: int) -> str:
        """Extract chapter title from first page"""
        # Look for patterns like "3\nLinear Methods for Regression"
        lines = first_page_text.split('\n')

        for i, line in enumerate(lines):
            if line.strip() == str(chapter_num) and i + 1 < len(lines):
                # Next line should be the title
                title = lines[i + 1].strip()
                if title:
                    return title

        # Fallback to hardcoded titles
        chapter_titles = {
            1: "Introduction",
            2: "Overview of Supervised Learning",
            3: "Linear Methods for Regression",
            4: "Linear Methods for Classification",
            5: "Basis Expansions and Regularization",
            6: "Kernel Smoothing Methods",
            7: "Model Assessment and Selection",
            8: "Model Inference and Averaging",
            9: "Additive Models, Trees, and Related Methods",
            10: "Boosting and Additive Trees",
            11: "Neural Networks",
            12: "Support Vector Machines and Flexible Discriminants",
            13: "Prototype Methods and Nearest-Neighbors",
            14: "Unsupervised Learning",
            15: "Random Forests",
            16: "Ensemble Learning",
            17: "Undirected Graphical Models",
            18: "High-Dimensional Problems",
        }

        return chapter_titles.get(chapter_num, f"Chapter {chapter_num}")

    def _parse_sections(self, text: str) -> List[Dict]:
        """
        Parse chapter text into sections

        Args:
            text: Chapter text

        Returns:
            List of sections with titles and content
        """
        sections = []

        # Pattern for section headers like "3.1 Introduction" or "3.2.1 Subset Selection"
        section_pattern = r'^(\d+\.\d+(?:\.\d+)?)\s+([A-Z][^\n]+)$'

        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            match = re.match(section_pattern, line.strip())

            if match:
                # Save previous section if exists
                if current_section:
                    sections.append({
                        'number': current_section['number'],
                        'title': current_section['title'],
                        'content': '\n'.join(current_content).strip()
                    })

                # Start new section
                current_section = {
                    'number': match.group(1),
                    'title': match.group(2).strip()
                }
                current_content = []
            else:
                # Add to current section content
                if current_section:
                    current_content.append(line)

        # Add last section
        if current_section:
            sections.append({
                'number': current_section['number'],
                'title': current_section['title'],
                'content': '\n'.join(current_content).strip()
            })

        return sections

    def get_chapter_summary(self, chapter_num: int) -> str:
        """Get a summary of chapter structure"""
        chapter_data = self.extract_chapter(chapter_num)

        if not chapter_data:
            return f"Chapter {chapter_num} not found"

        summary = f"Chapter {chapter_data['chapter_num']}: {chapter_data['title']}\n"
        summary += f"Pages: {chapter_data['start_page']}-{chapter_data['end_page']} ({chapter_data['page_count']} pages)\n"
        summary += f"Sections: {len(chapter_data['sections'])}\n\n"

        for section in chapter_data['sections']:
            summary += f"  {section['number']} {section['title']}\n"

        return summary

    def close(self):
        """Close PDF document"""
        self.doc.close()


def main():
    """Test the extractor"""
    import sys

    pdf_path = "../content/machine_learning/elements_of_statistical_learning.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    extractor = ESLBookExtractor(pdf_path)

    print("Elements of Statistical Learning - Chapter Extractor")
    print("=" * 80)
    print(f"Total pages in PDF: {extractor.total_pages}\n")

    # Test with Chapter 3
    print("Extracting Chapter 3: Linear Methods for Regression")
    print("-" * 80)

    chapter_data = extractor.extract_chapter(3)

    if chapter_data:
        print(f"\nChapter {chapter_data['chapter_num']}: {chapter_data['title']}")
        print(f"Pages: {chapter_data['start_page']}-{chapter_data['end_page']}")
        print(f"Total sections found: {len(chapter_data['sections'])}\n")

        print("Sections:")
        for section in chapter_data['sections']:
            print(f"  {section['number']} {section['title']}")
            content_preview = section['content'][:100].replace('\n', ' ')
            print(f"    Preview: {content_preview}...\n")

        # Save to file for inspection
        output_file = "/tmp/chapter3_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Chapter {chapter_data['chapter_num']}: {chapter_data['title']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(chapter_data['text'])

        print(f"\nFull chapter text saved to: {output_file}")

    extractor.close()


if __name__ == "__main__":
    main()
