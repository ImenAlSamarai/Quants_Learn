# 🧠 Quant Learning Platform - MVP v1.0

An intelligent, adaptive learning platform for aspiring quantitative finance professionals. Features AI-generated educational content that adapts to your learning level, beautiful mathematical rendering, and progress tracking across difficulty levels.

## ✨ MVP Features

### 🎓 **Adaptive Learning Levels**
- **5 Difficulty Levels**: From beginner to experienced researcher
- **Level-Specific Content**: Each topic generates different explanations for different levels
- **Independent Progress Tracking**: Complete topics at one level without affecting others

### 🧮 **Professional Mathematical Content**
- **LaTeX Rendering**: Beautiful mathematical formulas with KaTeX
- **Comprehensive Explanations**: Structured educational content with:
  - Core concepts with mathematical formulations
  - Real-world quantitative finance applications
  - Python implementation examples
  - Key takeaways
- **Syntax-Highlighted Code**: Python code snippets with VS Code Dark Plus theme

### 📊 **Learning Management**
- **Interactive Mind Maps**: Visualexploration of topic relationships
- **Progress Tracking**: Level-specific completion tracking
- **Smart Caching**: Instant loading for previously viewed content
- **Personalized Recommendations**: Suggested topics based on your progress

### 🗺️ **Core Content Categories**
- **Linear Algebra**: Vectors, matrices, eigenvalues, SVD, PCA
- **Calculus**: Multivariable calculus, optimization, differential equations
- **Probability**: Distributions, expectations, stochastic processes
- **Statistics**: Inference, regression, hypothesis testing

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

### Setting Your Learning Level

1. Click **⚙️ Settings** in the top navigation
2. Select your level:
   - **🌱 Undergraduate - New to Quant Finance**: Simple explanations, minimal equations
   - **📚 Undergraduate - Foundation**: Balanced intuition and formalism
   - **🎓 Graduate Student**: Strong math background, rigorous approach
   - **🔬 PhD Researcher**: Research-level examples, cutting-edge applications
   - **⭐ Experienced Researcher**: Technical depth, production implementations
3. Click **Save Preferences**

### Learning a Topic

1. **Choose a category** (Linear Algebra, Calculus, Probability, Statistics)
2. **Switch between views**:
   - **Study Mode**: Structured learning with explanations
   - **Explore Mode**: Visual mind map navigation
3. **Click a topic** to view content
4. **First-time load**: May take 30-60 seconds (LLM generation)
5. **Subsequent loads**: Instant (cached)
6. **Mark as complete** when finished

### Switching Levels

- Progress is tracked **separately per level**
- Completing "Eigenvalues" at Level 3 ≠ complete at Level 5
- Try the same topic at different levels to see adapted content!

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
- **Cache keys**: `node_id + content_type + difficulty_level`
- **Smart invalidation**: Clear cache script for testing

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
│   ├── scripts/
│   │   ├── index_content.py    # Content indexing
│   │   └── clear_cache.py      # Cache management
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

### Clearing Cache (For Testing)

```bash
cd backend

# View cache statistics
python scripts/clear_cache.py stats

# Clear all cached content
python scripts/clear_cache.py clear-all

# Clear specific difficulty level
python scripts/clear_cache.py clear-difficulty --difficulty 3

# Clear specific topic
python scripts/clear_cache.py clear-node --node-id 5
```

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

### ✅ MVP v1.0 (Current)
- [x] Level-specific content generation
- [x] LaTeX math rendering
- [x] Python code highlighting
- [x] Independent progress tracking
- [x] Smart caching
- [x] Mind map visualization

### 📅 v1.1 (Next)
- [ ] Examples mode (applied finance examples)
- [ ] Quiz mode (interactive quizzes)
- [ ] Visualization mode (interactive plots)
- [ ] User authentication
- [ ] More content topics

### 🔮 v2.0 (Future)
- [ ] Machine Learning content
- [ ] Code execution environment
- [ ] Collaborative features
- [ ] Mobile responsive design
- [ ] Offline mode

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

**MVP v1.0 - Ready for Testing** 🚀

*Built with ❤️ for aspiring quants*
