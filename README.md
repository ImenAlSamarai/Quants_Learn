# 🧠 Quant Learning Platform

An interactive, mind-map-driven learning platform designed to help aspiring quant researchers master quantitative finance through visual exploration, AI-powered explanations, and hands-on experiments.

## ✨ Features

- **🗺️ Interactive Mind Map**: Visually explore topics and their relationships
- **🧠 AI-Powered Explanations**: GPT-4 generates conceptual explanations tailored to your level
- **💡 Applied Examples**: Real-world applications in quant finance and physics
- **🧩 Interactive Visualizations**: Experiment with mathematical concepts dynamically
- **📊 Smart Quizzes**: Test understanding with AI-generated questions
- **🔍 RAG-Based Search**: Semantic search across all learning materials
- **📈 Progress Tracking**: Monitor your learning journey

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  Mind Map Visualization • Content Viewer • Quizzes          │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  • Node Management  • Content Query  • Progress Tracking    │
└────┬──────────────────────────────────────────┬─────────────┘
     │                                           │
     ▼                                           ▼
┌────────────────┐                    ┌──────────────────────┐
│   PostgreSQL   │                    │  Pinecone Vector DB  │
│ Node metadata  │                    │  Embeddings + chunks │
│ Relationships  │                    │  Semantic search     │
└────────────────┘                    └──────────────────────┘
                                                │
                                                ▼
                                      ┌──────────────────┐
                                      │  OpenAI GPT-4    │
                                      │  • Embeddings    │
                                      │  • Generation    │
                                      └──────────────────┘
```

## 📚 Learning Modules

### Core Foundations (MVP)
- **Linear Algebra**: Vectors, matrices, eigenvalues, SVD, PCA
- **Calculus**: Derivatives, integrals, optimization
- **Probability**: Distributions, expectations, limit theorems
- **Statistics**: Inference, hypothesis testing, regression

### Coming Soon
- Machine Learning
- Deep Learning
- Time Series Analysis
- Derivatives Pricing
- Portfolio Theory

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Pinecone account (free tier available)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/quant-learning-platform.git
cd quant-learning-platform
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys:
#   - PINECONE_API_KEY
#   - OPENAI_API_KEY
#   - DATABASE_URL

# Initialize database
python -c "from app.models.database import init_db; init_db()"

# Index sample content
python scripts/index_content.py --init-db --content-dir ../content

# Start backend server
python -m app.main
```

The backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Access the Platform

Open your browser and navigate to `http://localhost:3000`

## 📖 Detailed Setup Guide

### Database Configuration

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database**:
   ```bash
   createdb quant_learn
   ```

3. **Update DATABASE_URL** in `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/quant_learn
   ```

### Pinecone Setup

1. Sign up at [https://www.pinecone.io/](https://www.pinecone.io/)
2. Create a new index:
   - **Name**: `quant-learning`
   - **Dimensions**: `1536` (for text-embedding-3-small)
   - **Metric**: `cosine`
   - **Cloud**: AWS or GCP (free tier)
3. Copy your API key to `.env`:
   ```
   PINECONE_API_KEY=your-api-key-here
   ```

### OpenAI Setup

1. Get API key from [https://platform.openai.com/](https://platform.openai.com/)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

## 🎨 Usage

### Exploring Topics

1. **Select a Category**: Choose from Linear Algebra, Calculus, Probability, or Statistics
2. **Navigate the Mind Map**: Click on nodes to explore topics
3. **View Content**: Each node offers:
   - 🧠 **Explanation**: Conceptual understanding
   - 💡 **Examples**: Applied use cases in quant finance
   - 🧩 **Quiz**: Test your knowledge
   - 📊 **Visualization**: Interactive experiments

### Adding Custom Content

1. **Create Markdown File** in `content/` directory:
   ```markdown
   ---
   title: Your Topic
   category: linear_algebra
   subcategory: advanced
   difficulty: 3
   ---

   # Your Topic

   Content here...
   ```

2. **Update Indexing Script** in `backend/scripts/index_content.py`:
   ```python
   node_id = indexer.index_node(
       title="Your Topic",
       category="linear_algebra",
       subcategory="advanced",
       content_path="path/to/your/file.md",
       difficulty=3,
       x_pos=0,
       y_pos=0,
       parent_ids=[parent_node_id]
   )
   ```

3. **Re-index Content**:
   ```bash
   python scripts/index_content.py
   ```

## 🔧 API Endpoints

### Nodes

- `GET /api/nodes/mindmap?category={category}` - Get mind map structure
- `GET /api/nodes/{node_id}` - Get node details
- `POST /api/nodes` - Create new node (admin)

### Content

- `POST /api/content/query` - Query content with LLM generation
  ```json
  {
    "node_id": 1,
    "query_type": "explanation|example|quiz|visualization",
    "user_context": "optional context"
  }
  ```

- `GET /api/content/search?query={query}&category={category}` - Semantic search

### Progress

- `GET /api/progress/user/{user_id}` - Get user progress
- `POST /api/progress/update` - Update progress
- `GET /api/progress/user/{user_id}/recommendations` - Get personalized recommendations

## 🏛️ Project Structure

```
quant-learning-platform/
├── backend/
│   ├── app/
│   │   ├── config/          # Settings and configuration
│   │   ├── models/          # Database models and schemas
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic (LLM, vector store)
│   │   └── main.py          # FastAPI application
│   ├── scripts/
│   │   └── index_content.py # Content indexing pipeline
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── styles/          # CSS
│   │   ├── App.jsx          # Main app
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
├── content/
│   ├── linear_algebra/      # Learning content (markdown)
│   ├── calculus/
│   ├── probability/
│   └── statistics/
└── README.md
```

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
npm run format
```

### Building for Production

```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm run preview
```

## 🎯 Technology Choices & Rationale

### Backend: FastAPI
- **Why**: Modern, fast, automatic API docs, excellent async support
- **Alternatives**: Flask (simpler but less features), Django (overkill for this use case)

### Frontend: React + Vite
- **Why**: Component-based, large ecosystem, fast dev experience with Vite
- **Alternatives**: Vue (simpler learning curve), Svelte (smaller bundle)

### Mind Map: react-force-graph-2d
- **Why**: Physics-based layout, interactive, customizable rendering
- **Alternatives**: D3.js (more control but complex), vis.js (heavier)

### Vector Database: Pinecone
- **Why**: Managed, scalable, excellent for RAG applications
- **Alternatives**: Weaviate, Qdrant, Milvus (self-hosted options)

### LLM: OpenAI GPT-4
- **Why**: State-of-the-art reasoning, good for educational content
- **Alternatives**: Claude (Anthropic), open-source models via Ollama

### Visualizations: Plotly.js
- **Why**: Interactive, publication-quality, supports 2D/3D
- **Alternatives**: D3.js (more control), Chart.js (simpler)

## 📈 Roadmap

### Phase 1: MVP (Current)
- [x] Core architecture
- [x] Linear Algebra content
- [x] Mind map visualization
- [x] AI-powered explanations
- [x] Interactive quizzes
- [x] Basic visualizations

### Phase 2: Enhancement
- [ ] More learning modules (ML, DL)
- [ ] User authentication
- [ ] Advanced visualizations
- [ ] Code execution environment (Jupyter integration)
- [ ] Collaborative features

### Phase 3: Scale
- [ ] Mobile app
- [ ] Offline mode
- [ ] Community contributions
- [ ] Certification system

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add your content or features
4. Submit a pull request

## 📄 License

MIT License - feel free to use this for your learning journey!

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embeddings
- Pinecone for vector database
- The quantitative finance community

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Happy Learning! 🚀📊**
