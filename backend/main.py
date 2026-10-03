import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.api.routes import (
    auth_routes,
    agent_routes,
    policy_routes,
    customer_routes,
    llm_routes,
    sse_routes,
    chat_routes,
)
from backend.utils.logger import get_logger
from backend.api.dependencies import verify_jwt

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Enterprise-ready Customer 360 API",
        version="1.0.0",
    )

    from fastapi import Request
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_routes.router, prefix="/api/v1")
    app.include_router(sse_routes.router, prefix="/api/v1")
    app.include_router(
        agent_routes.router, prefix="/api/v1", dependencies=[Depends(verify_jwt)]
    )
    app.include_router(
        policy_routes.router, prefix="/api/v1", dependencies=[Depends(verify_jwt)]
    )
    app.include_router(
        customer_routes.router, prefix="/api/v1", dependencies=[Depends(verify_jwt)]
    )
    app.include_router(
        chat_routes.router, prefix="/api/v1", dependencies=[Depends(verify_jwt)]
    )
    app.include_router(llm_routes.router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} Server...")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {settings.app_name} Server...")

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "app": settings.app_name}

    @app.get("/", tags=["Health"])
    def root_health_check():
        return {"status": "ok", "message": f"Welcome to {settings.app_name} API"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
