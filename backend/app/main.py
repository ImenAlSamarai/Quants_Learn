from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.models.database import init_db
from app.routes import nodes, content, progress, users, admin, insights
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Interactive mind-map driven learning platform for aspiring quant researchers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nodes.router)
app.include_router(content.router)
app.include_router(progress.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(insights.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print(f"Server starting at http://localhost:8000")
    print(f"API docs available at http://localhost:8000/docs")


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "features": {
            "caching": "enabled",
            "difficulty_levels": "1-5",
            "admin_panel": "enabled"
        },
        "endpoints": {
            "nodes": "/api/nodes",
            "mindmap": "/api/nodes/mindmap",
            "content": "/api/content (with caching)",
            "progress": "/api/progress",
            "users": "/api/users",
            "admin": "/api/admin"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
