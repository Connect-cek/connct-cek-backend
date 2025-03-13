from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .routers import (
    auth,
    users,
    admin,
    posts,
    messages,
    resume,
    institutions,
    super_admin,
)
from .database import Base, engine
import time
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from fastapi.responses import JSONResponse

# Create the database tables
Base.metadata.create_all(bind=engine)

# Custom middleware for request timing and logging
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "process_time": process_time
                }
            )

app = FastAPI(
    title="Connect - Alumni Student Platform",
    description="API for the Connect alumni student platform",
    version="1.0.0",
    docs_url="/api/docs",  # Change Swagger UI path
    redoc_url="/api/redoc",  # Change ReDoc path
)

# CORS configuration with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["X-Process-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add security middlewares
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TimingMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(messages.router)
app.include_router(resume.router)
app.include_router(institutions.router)
app.include_router(super_admin.router)

@app.get("/")
async def root():
    """Root endpoint returning welcome message"""
    return {
        "message": "Welcome to the Connect API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "database": "connected" if engine else "disconnected"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path,
            "method": request.method
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)