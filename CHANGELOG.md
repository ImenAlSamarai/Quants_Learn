# Changelog

All notable changes to the Quant Learning Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-17 - MVP Release

### 🎉 MVP Features

#### Adaptive Learning System
- **5 Difficulty Levels**: Undergraduate (Beginner & Foundation), Graduate, PhD Researcher, Experienced Researcher
- **Level-Specific Content Generation**: Each topic generates unique explanations adapted to user's expertise
- **Independent Progress Tracking**: Separate completion tracking for each difficulty level
- **User Settings Persistence**: Learning level and background saved to database

#### Professional Educational Content
- **LaTeX Math Rendering**: Beautiful formula rendering using KaTeX
  - Inline math: `$E[X] = \mu$`
  - Display math: centered equations with proper spacing
- **Syntax-Highlighted Code**: Python code examples with VS Code Dark Plus theme
- **Structured Content Format**:
  - Core Concept: Fundamental explanations
  - Mathematical Formulation: Key equations and notation
  - Quantitative Finance Application: Real-world use cases
  - Python Implementation: Working code examples
  - Key Takeaways: Bullet-point summaries

#### Enhanced LLM Integration
- **Comprehensive Prompts**: Eliminates filler phrases, focuses on direct educational content
- **Level-Appropriate Language**: Mathematical rigor matches user expertise
- **Practical Focus**: Every topic includes quant finance applications
- **Smart Caching**:
  - First generation: 30-60 seconds (OpenAI API call)
  - Cached retrieval: <1 second (database lookup)
  - Cache keys: `node_id + content_type + difficulty_level`

#### User Interface
- **Interactive Mind Map**: Visual exploration of topic relationships (react-force-graph-2d)
- **Dual-Mode Navigation**:
  - Study Mode: Linear, structured learning
  - Explore Mode: Visual mind map navigation
- **Progress Dashboard**: Real-time statistics and recommendations
- **Responsive Design**: Clean, modern interface with Tailwind CSS v4

#### Content Library
- **4 Core Categories**: Linear Algebra, Calculus, Probability, Statistics
- **19 Topics**: Comprehensive coverage of quantitative finance fundamentals
- **RAG Pipeline**: Pinecone vector database for semantic search and context retrieval

### 🔧 Technical Implementation

#### Backend (FastAPI)
- **Content Generation Service**: OpenAI GPT-4o-mini integration
- **Vector Store Service**: Pinecone for embeddings and semantic search
- **Caching Layer**: PostgreSQL-based content cache
- **User Management**: Learning level and progress tracking
- **API Documentation**: Auto-generated with FastAPI Swagger UI

#### Frontend (React + Vite)
- **State Management**: Zustand for global state
- **Markdown Rendering**: react-markdown with plugins
- **Math Support**: remark-math + rehype-katex
- **Code Highlighting**: react-syntax-highlighter with Prism
- **API Client**: Axios with 60-second timeout for LLM calls

#### Database Schema
- **Nodes**: Topics with metadata, positioning, difficulty
- **Edges**: Prerequisites and topic relationships
- **Users**: Learning level, background, preferences
- **Progress**: Completion tracking, quiz scores, time spent
- **Generated Content**: Cached LLM responses with versioning

### 🐛 Fixes

#### Content Display
- Removed redundant "Related Content" and "Explore Further" sections
- Fixed raw text chunks appearing in content area
- Proper markdown rendering replaces dangerous HTML injection

#### Progress Tracking
- Fixed completions affecting all difficulty levels
- Implemented per-level completion storage (`"topicId-level"` keys)
- Updated all components to use `isTopicCompleted()` helper

#### Performance
- Increased API timeout from 30s to 60s for LLM generation
- Fixed Python f-string syntax errors in prompts
- Optimized cache lookup queries

#### Code Quality
- Removed backup files (`.old.jsx`, `.FIXED.css`)
- Updated `.env.example` to use `gpt-4o-mini`
- Cleaned up debug code and console logs

### 🛠️ Developer Tools

#### Scripts
- `clear_cache.py`: Manage cached content
  - `stats`: View cache statistics
  - `clear-all`: Delete all cached content
  - `clear-difficulty --difficulty N`: Clear specific level
  - `clear-node --node-id N`: Clear specific topic

#### Documentation
- `README.md`: Comprehensive project overview
- `TESTING_GUIDE.md`: Test scenarios for QA/user testing
- `CHANGELOG.md`: Version history and release notes

### 📦 Dependencies

#### Backend
- fastapi==0.104.1
- openai==1.3.5
- pinecone-client==2.2.4
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- python-dotenv==1.0.0

#### Frontend
- react==18.2.0
- vite==5.0.11
- axios==1.6.5
- zustand==5.0.8
- katex==0.16.9
- react-markdown==9.0.1
- remark-math==6.0.0
- rehype-katex==7.0.0
- react-syntax-highlighter==15.5.0
- react-force-graph-2d==1.25.4
- framer-motion==12.23.24
- tailwindcss==4.1.17

### 🎯 Performance Metrics

- **Initial Page Load**: ~2-3 seconds
- **Topic Navigation**: <500ms (cached) / 30-60s (first generation)
- **Mind Map Rendering**: <1 second for 20 nodes
- **Cache Hit Rate**: ~95% after initial content generation
- **Average Content Length**: 500-800 words per topic

### 🔒 Security

- Environment variables for all API keys
- SQL injection protection via SQLAlchemy ORM
- XSS protection with proper markdown sanitization
- CORS configured for development

### 📝 Known Limitations

- No user authentication (uses demo_user)
- Limited to 4 content categories
- Only "explanation" content type fully implemented
- No mobile optimization
- Single-user mode (no multi-tenancy)

### 🔮 Future Roadmap

See `README.md` for v1.1 and v2.0 planned features.

---

## Release Notes

### v1.0.0 - MVP Release (November 17, 2024)

This is the first production-ready release of the Quant Learning Platform. It includes:

✅ **Core Learning Features**: 5-level adaptive content, math rendering, code examples
✅ **Progress Tracking**: Independent tracking per difficulty level
✅ **Smart Caching**: Sub-second load times for cached content
✅ **Professional UI**: Clean, modern interface with mind map visualization
✅ **19 Topics**: Comprehensive coverage of quant finance fundamentals

This MVP is ready for user testing and feedback gathering.

### Installation

See `README.md` for detailed installation instructions.

### Upgrade Path

This is the first release, no upgrade path needed.

### Breaking Changes

None (first release).

### Contributors

- Imen Al Samarai - Initial development and MVP implementation

---

**Questions or Issues?**

Open an issue on [GitHub](https://github.com/ImenAlSamarai/Quants_Learn/issues)

**License**: MIT - See LICENSE file for details
