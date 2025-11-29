# Content Directory

This directory should contain PDF books for content generation.

## Adding Books

1. Place PDF files in this directory
2. Use descriptive names with underscores: `Advances_in_Financial_Machine_Learning.pdf`
3. Run indexing script to make them searchable

## Example Structure

```
content/
├── Advances_in_Financial_Machine_Learning.pdf
├── Elements_of_Statistical_Learning.pdf
├── Quantitative_Risk_Management.pdf
└── Time_Series_Analysis_Hamilton.pdf
```

## Indexing

After adding a PDF:

```bash
cd /home/user/Quants_Learn/backend
python scripts/index_pdfs.py
```

This will:
- Extract text from PDFs
- Chunk them intelligently (respecting chapters)
- Create embeddings
- Store in ChromaDB for semantic search

## Supported Books (Recommended)

See `backend/app/services/learning_path_service.py` for the full list of curated book recommendations organized by topic.

### Alpha Research & Trading
- **Advances in Financial Machine Learning** by Marcos López de Prado (2018)
- Machine Learning for Asset Managers by Marcos López de Prado (2020)

### Options & Derivatives
- Options, Futures, and Other Derivatives by John Hull (2021)
- The Concepts and Practice of Mathematical Finance by Mark Joshi (2008)

### Risk Management
- Quantitative Risk Management by McNeil, Frey & Embrechts (2015)

### Time Series
- Analysis of Financial Time Series by Ruey S. Tsay (2010)
- Time Series Analysis by Hamilton (1994)

### Machine Learning Foundations
- Elements of Statistical Learning by Hastie, Tibshirani & Friedman (2009)
- Pattern Recognition and Machine Learning by Christopher Bishop (2006)

## Book Metadata

PDFs are chunked with metadata:
```json
{
  "source": "Advances_in_Financial_Machine_Learning",
  "chapter": "Chapter 3",
  "section": "Labeling Methods",
  "page": 45,
  "text": "... chunk content ..."
}
```

## Coverage Detection

When a user submits a job description:
1. GPT extracts topics (e.g., "alpha generation")
2. System queries ChromaDB for relevant chunks
3. If similarity score > 0.45 → topic is COVERED ✅
4. Content can be generated using these chunks

## Next Steps

1. Add your first PDF
2. Run indexing script
3. Submit a job description
4. Verify topic coverage
