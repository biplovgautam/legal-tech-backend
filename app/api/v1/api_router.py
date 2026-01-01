from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "message": "Legal Tech API is running"
    }
