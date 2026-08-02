from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database.database import init_db
from utils.logger import logger

# Import API Routers
from api.routes.auth import router as auth_router
from api.routes.claims import router as claims_router
from api.routes.documents import router as documents_router
from api.routes.explanation import router as explanation_router
from api.routes.ops_cases import router as ops_cases_router
from api.routes.ops_decisions import router as ops_decisions_router
from api.routes.analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} backend...")
    init_db()
    logger.info("Database tables initialized successfully.")
    yield
    logger.info("Shutting down Claims Adjudication Platform backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent Claims Adjudication Platform powered by Python, FastAPI, LangChain, and LangGraph.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(claims_router, prefix=api_v1_prefix)
app.include_router(documents_router, prefix=api_v1_prefix)
app.include_router(explanation_router, prefix=api_v1_prefix)
app.include_router(ops_cases_router, prefix=api_v1_prefix)
app.include_router(ops_decisions_router, prefix=api_v1_prefix)
app.include_router(analytics_router, prefix=api_v1_prefix)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV
    }
