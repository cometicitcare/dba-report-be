"""
Buddhist Affairs MIS Dashboard - Application Runner
"""
import uvicorn

if __name__ == "__main__":
    # Note: In production, use Procfile instead (Railway deployment)
    # For local development only:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development only
        log_level="info",
    )
