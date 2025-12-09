# 🧠 Quant Learning Platform - Job-Based Personalization

An intelligent, job-focused learning platform for aspiring quantitative finance professionals. Paste any quant job description and get a personalized learning path with AI-generated content, mathematical rendering, and progress tracking.

## ✨ Key Features

### 🎯 **Job-Based Personalization**
- **Paste Any Job Description**: Analyze requirements from real job postings
- **Automatic Topic Extraction**: AI identifies explicit and implicit skills needed
- **Staged Learning Paths**: Topics organized in logical progression stages
- **Coverage Calculation**: See what % of job requirements you've mastered

### 🧮 **Professional Content Generation**
- **LaTeX Rendering**: Beautiful mathematical formulas with KaTeX
- **AI-Powered Explanations**: GPT-4 generated content for each topic with:
  - Core concepts with mathematical formulations
  - Real-world quantitative finance applications
  - Python implementation examples
  - Key takeaways
- **Syntax-Highlighted Code**: Python snippets with VS Code Dark Plus theme
- **External Resources**: Curated papers, tutorials, and references

### 📊 **Learning Management**
- **Interactive Mind Maps**: Visual exploration of topic relationships
- **Progress Tracking**: Mark topics complete as you learn
- **Smart Caching**: Instant loading for previously viewed content
- **Recommended Resources**: External learning materials for each topic

### 🗺️ **Core Content Categories**
- **Linear Algebra**: Vectors, matrices, eigenvalues, SVD, PCA
- **Calculus**: Multivariable calculus, optimization, differential equations
- **Probability**: Distributions, expectations, stochastic processes
- **Statistics**: Inference, regression, hypothesis testing, time series

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+**
- **Pinecone account** ([free tier](https://www.pinecone.io/))
- **OpenAI API key** ([get one here](https://platform.openai.com/))

### 1. Clone Repository

```bash
git clone https://github.com/ImenAlSamarai/Quants_Learn.git
cd Quants_Learn
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys:
#   OPENAI_API_KEY=sk-your-key
#   PINECONE_API_KEY=your-key
#   DATABASE_URL=postgresql://user:pass@localhost:5432/quant_learn

# Initialize database and index content
python -c "from app.models.database import init_db; init_db()"
python scripts/index_content.py --init-db --content-dir ../content

# Verify system health
python manage.py health-check

# Start server
python -m app.main
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

## 📖 User Guide

### Creating a Learning Path from a Job Description

1. **Navigate to Home Page** - Click "Quant Learning Platform" logo or home button
2. **Paste Job Description** - Copy/paste the full job posting text into the text area
3. **Click "Analyze Job & Generate Path"** - Wait 10-30 seconds for AI analysis
4. **Review Learning Path**:
   - **Stages**: Topics organized in logical progression (Fundamentals → Advanced)
   - **Priority**: High-priority topics highlighted in red
   - **Coverage**: See % of job requirements covered by available content
5. **Start Learning**:
   - Click any topic to view AI-generated content
   - First load: 30-60 seconds (LLM generation)
   - Subsequent loads: Instant (cached)
6. **Track Progress**: Mark topics complete as you master them

### Exploring Topics with Mind Map

1. **Switch to Explore Mode** - Toggle between Study and Explore views
2. **Visual Navigation** - Interactive force-directed graph shows topic relationships
3. **Click nodes** to view content
4. **Zoom and pan** to explore connections

### Using External Resources

- Each topic includes curated external resources (papers, tutorials, courses)
- Click links to access original materials
- Resources are ranked by relevance to the specific job requirements

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             Frontend (React + Vite)                         │
│  • Interactive Mind Map (react-force-graph-2d)              │
│  • LaTeX Rendering (KaTeX)                                  │
│  • Code Highlighting (react-syntax-highlighter)             │
│  • State Management (Zustand)                               │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API (Axios)
┌──────────────────▼──────────────────────────────────────────┐
│              Backend (FastAPI + Python)                     │
│  • Content Generation (OpenAI GPT-4o-mini)                  │
│  • Caching (PostgreSQL)                                     │
│  • RAG Pipeline (Pinecone + embeddings)                     │
│  • User Management & Progress                               │
└───┬──────────────────────────────────────┬─────────────────┘
    │                                       │
    ▼                                       ▼
┌──────────────────┐            ┌────────────────────────────┐
│   PostgreSQL     │            │   Pinecone Vector DB       │
│ • Nodes/topics   │            │ • Content embeddings       │
│ • Users          │            │ • Semantic search          │
│ • Progress       │            │ • Context chunks           │
│ • Cache          │            └────────────────────────────┘
└──────────────────┘                        │
                                            ▼
                                ┌────────────────────────┐
                                │   OpenAI API           │
                                │ • text-embedding-3-small│
                                │ • gpt-4o-mini          │
                                └────────────────────────┘
```

## 🎯 MVP Highlights

### Intelligent Content Caching
- **First load**: 30-60 seconds (LLM generation)
- **Cache hit**: <1 second (database retrieval)
- **Cache keys**: `node_id + content_type + difficulty_level + content_version`
- **Automatic invalidation**: Cache auto-invalidates when content is updated (version tracking)
- **No manual clearing needed**: Update content with `manage.py update-content`

### Enhanced Educational Prompts
- **No filler content**: Directly starts with concepts
- **Structured format**: Consistent sections across all topics
- **Level-appropriate**: Mathematical rigor matches user expertise
- **Practical focus**: Every topic includes quant finance applications
- **Code examples**: Working Python snippets for implementation

### Professional Math Rendering
- **Inline math**: `$E[X] = \mu$`
- **Display math**: `$$\int_{-\infty}^{\infty} f(x)dx = 1$$`
- **Responsive**: Adapts to screen size
- **Copy-friendly**: Can select and copy formulas

## 🛠️ Development

### Project Structure

```
Quants_Learn/
├── backend/
│   ├── app/
│   │   ├── config/         # Settings
│   │   ├── models/         # Database models & schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # LLM & vector store logic
│   │   └── main.py         # FastAPI app
│   ├── management/
│   │   └── commands/       # CLI commands (health-check, update-content, etc.)
│   ├── scripts/
│   │   └── index_content.py    # Initial content indexing
│   ├── manage.py           # Management CLI entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── study/      # Study mode
│   │   │   ├── explore/    # Mind map
│   │   │   ├── discovery/  # Landing page
│   │   │   └── layout/     # Header, sidebar
│   │   ├── services/       # API client
│   │   ├── store/          # Zustand state
│   │   ├── styles/         # CSS
│   │   └── App.jsx
│   └── package.json
└── content/                # Learning materials (markdown)
```

### Management CLI

The platform includes a unified management CLI for all operational tasks:

```bash
cd backend

# Check system health (database, Pinecone, content indexing)
python manage.py health-check
python manage.py health-check --verbose  # Detailed output

# Update content (automatic cache invalidation)
python manage.py update-content --node-id 17
python manage.py update-content --node-id 17 --verify  # With verification

# Inspect cache (debug)
python manage.py clear-cache --node-id 17 --inspect

# Clear cache (rarely needed - cache auto-invalidates on content update)
python manage.py clear-cache --node-id 17
python manage.py clear-cache --category statistics
python manage.py clear-cache --all

# Generate missing insights
python manage.py generate-insights --category statistics
python manage.py generate-insights --all
```

**Note:** Cache automatically invalidates when content is updated via `update-content`. Manual cache clearing is rarely needed.

### API Endpoints

#### Content Generation
```bash
POST /api/content/query
{
  "node_id": 1,
  "query_type": "explanation",
  "user_id": "demo_user",
  "force_regenerate": false
}
```

#### Mind Map
```bash
GET /api/nodes/mindmap?category=linear_algebra
```

#### User Settings
```bash
GET /api/users/{user_id}
PATCH /api/users/{user_id}
{
  "learning_level": 3,
  "background": "Physics PhD"
}
```

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/quant_learn

# Pinecone
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=quant-learning

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini

# App
APP_NAME=Quant Learning Platform
DEBUG=True
```

**Frontend**: No env vars required (uses `http://localhost:8000` by default)

## 🐛 Troubleshooting

### "timeout of 60000ms exceeded"
- **Cause**: LLM taking too long to generate content
- **Solution**: Wait up to 60 seconds. Subsequent loads are instant.
- **Note**: First generation for new topics/levels is always slower

### "Cache MISS" in backend logs
- **Normal behavior**: Content not yet generated for this topic + level
- **Expected**: Shows cache generation progress
- **Solution**: Wait for "Content cached" message

### Math formulas not rendering
- **Cause**: Missing LaTeX packages
- **Solution**: Run `npm install` in frontend directory
- **Check**: Verify `katex`, `remark-math`, `rehype-katex` installed

### Code blocks not highlighted
- **Cause**: Missing syntax highlighter
- **Solution**: Run `npm install react-syntax-highlighter`

## 📊 MVP Metrics

- **Content Categories**: 4 (Linear Algebra, Calculus, Probability, Statistics)
- **Topics**: 19 total
- **Difficulty Levels**: 5 (fully implemented)
- **Content Types**: Explanations (examples, quizzes, visualizations in roadmap)
- **Average Generation Time**: 15-30 seconds (first time)
- **Average Load Time**: <1 second (cached)

## 🗺️ Roadmap

### ✅ Phase 1-3: Complete
- [x] **Phase 1**: Difficulty-based content system (deprecated)
- [x] **Phase 2**: Backend job-based personalization
  - Job description analysis and topic extraction
  - Staged learning path generation
  - Coverage calculation
- [x] **Phase 3**: Frontend job-based UI
  - Job input and analysis interface
  - Visual learning path display
  - Progress tracking

### 🚧 Phase 4: Quality Improvements (Current)
- [x] Topic extraction improvements (80% specificity achieved)
- [ ] Upgrade to GPT-4o for better topic quality
- [ ] Enhanced content generation
- [ ] Improved resource recommendations
- [ ] Performance optimizations

### 📅 Future Enhancements
- [ ] User authentication and saved learning paths
- [ ] Quiz mode (interactive assessments)
- [ ] Code execution environment
- [ ] Mobile responsive design
- [ ] Collaborative features

## 📄 License

MIT License - Use freely for your learning journey!

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini and embeddings
- **Pinecone** for vector database
- **KaTeX** for beautiful math rendering
- **FastAPI** for excellent API framework
- **React** and the amazing frontend ecosystem

## 📧 Contact

For questions, feature requests, or bug reports:
- **GitHub Issues**: [Create an issue](https://github.com/ImenAlSamarai/Quants_Learn/issues)
- **Email**: Your contact info here

---

**Phase 3 Complete - Job-Based Personalization Live** 🚀

*Built with ❤️ for aspiring quants*
