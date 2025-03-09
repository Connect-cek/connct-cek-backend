from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, admin, posts, messages, resume, suggestions
from .database import Base, engine

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Connect - Alumni Student Platform",
    description="API for the Connect alumni student platform",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(messages.router)
app.include_router(resume.router)
app.include_router(suggestions.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Connect API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}