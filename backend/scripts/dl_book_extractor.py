"""
PDF Content Extractor for Deep Learning: Foundations and Concepts

This module extracts structured content from the Deep Learning book,
including chapters, sections, and mathematical content.

Similar to ESL extractor but adapted for Deep Learning book structure.
"""

import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class DeepLearningBookExtractor:
    """Extract content from Deep Learning: Foundations and Concepts PDF"""

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
            chapter_num: Chapter number

        Returns:
            Tuple of (start_page, end_page) or None if not found
        """
        # This will need to be determined by analyzing the actual PDF
        # Placeholder mapping - update after PDF analysis
        chapter_mapping = {
            # To be filled after analyzing the PDF structure
            # Format: chapter_num: (start_page, end_page)
        }

        return chapter_mapping.get(chapter_num)

    def detect_chapter_structure(self):
        """
        Analyze PDF to detect chapter structure

        Helper method to determine chapter boundaries
        """
        print(f"Analyzing PDF structure: {self.total_pages} pages")
        print("\nSearching for chapter markers...")

        chapter_pattern = r'^Chapter\s+(\d+)'

        found_chapters = []

        for page_num in range(min(50, self.total_pages)):  # Check first 50 pages
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')

            for line in lines:
                match = re.match(chapter_pattern, line.strip())
                if match:
                    chapter_num = int(match.group(1))
                    print(f"  Found Chapter {chapter_num} on page {page_num + 1}")
                    found_chapters.append((chapter_num, page_num))

        return found_chapters

    def extract_chapter(self, chapter_num: int, start_page: int = None, end_page: int = None) -> Optional[Dict]:
        """
        Extract a complete chapter with metadata

        Args:
            chapter_num: Chapter number
            start_page: Optional override for start page (0-indexed)
            end_page: Optional override for end page (0-indexed)

        Returns:
            Dictionary with chapter data
        """
        if start_page is None or end_page is None:
            pages = self.find_chapter_pages(chapter_num)
            if not pages:
                print(f"Chapter {chapter_num} not mapped. Use start_page and end_page arguments.")
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
        lines = first_page_text.split('\n')

        # Look for "Chapter N" followed by title
        for i, line in enumerate(lines):
            if re.match(f'^Chapter\\s+{chapter_num}', line.strip()):
                if i + 1 < len(lines):
                    title = lines[i + 1].strip()
                    if title:
                        return title

        # Fallback titles based on common DL book structure
        common_titles = {
            1: "Introduction",
            2: "Neural Networks",
            3: "Training Neural Networks",
            4: "Convolutional Networks",
            5: "Recurrent Networks",
            6: "Transformers and Attention",
            7: "Generative Models",
            8: "Reinforcement Learning",
        }

        return common_titles.get(chapter_num, f"Chapter {chapter_num}")

    def _parse_sections(self, text: str) -> List[Dict]:
        """
        Parse chapter text into sections

        Args:
            text: Chapter text

        Returns:
            List of sections with titles and content
        """
        sections = []

        # Pattern for section headers (adjust based on actual book format)
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

    def get_chapter_summary(self, chapter_num: int, start_page: int = None, end_page: int = None) -> str:
        """Get a summary of chapter structure"""
        chapter_data = self.extract_chapter(chapter_num, start_page, end_page)

        if not chapter_data:
            return f"Chapter {chapter_num} not found or not mapped"

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

    pdf_path = "../content/machine_learning/deep_learning_foundations_and_concepts.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found at {pdf_path}")
        print("Please add the PDF to content/machine_learning/ directory")
        sys.exit(1)

    extractor = DeepLearningBookExtractor(pdf_path)

    print("Deep Learning: Foundations and Concepts - Book Analyzer")
    print("=" * 80)
    print(f"Total pages in PDF: {extractor.total_pages}\n")

    # Detect chapter structure
    print("Detecting chapter structure...")
    chapters = extractor.detect_chapter_structure()

    if chapters:
        print(f"\nFound {len(chapters)} chapters")
        print("\nUpdate the find_chapter_pages() mapping with these values:")
        print("chapter_mapping = {")
        for i, (ch_num, page_num) in enumerate(chapters):
            if i + 1 < len(chapters):
                next_page = chapters[i + 1][1]
                print(f"    {ch_num}: ({page_num}, {next_page - 1}),")
            else:
                print(f"    {ch_num}: ({page_num}, {extractor.total_pages - 1}),")
        print("}")
    else:
        print("\nNo chapters detected automatically.")
        print("Manual analysis needed.")

    extractor.close()


if __name__ == "__main__":
    main()
