# Quick Start Guide

This guide will help you get the Quant Learning Platform up and running quickly.

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.9+ (for backend - optional for demo mode)
- PostgreSQL 13+ (optional - only needed if using full backend)

## Quick Start (Frontend Only - Demo Mode)

The frontend will work with demo data if the backend is not available.

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start Frontend Development Server

```bash
npm run dev
```

The application will open at `http://localhost:5173` (Vite default port).

**Note**: The app will automatically use demo data when the backend is unavailable. You can explore the interface and navigation without setting up the full backend.

## Full Stack Setup (Backend + Frontend)

For AI-powered explanations and full functionality:

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OpenAI, Pinecone, Database URL)

# Initialize database
python -c "from app.models.database import init_db; init_db()"

# Index content
python scripts/index_content.py --init-db --content-dir ../content

# Start backend
python -m app.main
```

Backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

## Features Available

### Demo Mode (No Backend)
- ✅ Browse categories (Linear Algebra, Calculus, Probability, Statistics)
- ✅ View topic hierarchies
- ✅ Navigate through topics
- ✅ See demo content
- ❌ AI-powered explanations
- ❌ Personalized quizzes
- ❌ Progress tracking

### Full Mode (With Backend)
- ✅ All demo features
- ✅ AI-powered explanations via GPT-4
- ✅ Interactive quizzes
- ✅ Semantic search
- ✅ Progress tracking
- ✅ Personalized recommendations

## Design Features

- 🎨 Clean cream & sage color palette
- 📱 Responsive design
- 🌓 Smooth animations with Framer Motion
- 🗺️ Interactive mind maps
- 📊 Progress visualization

## Troubleshooting

### CSS Import Error
If you see `@import must precede all other statements`, this has been fixed in the latest version.

### Content Not Loading
- Check that the backend is running if you need full features
- In demo mode, content should load automatically with sample data

### Port Conflicts
- Frontend default: `http://localhost:5173` (can be changed in vite.config.js)
- Backend default: `http://localhost:8000` (can be changed in backend/app/main.py)

## Next Steps

1. Explore the landing page and categories
2. Click on a category to see topics
3. Toggle between Study and Explore modes
4. (With backend) Try AI-generated explanations and quizzes

## Need Help?

Check the main README.md for detailed architecture and setup instructions.
