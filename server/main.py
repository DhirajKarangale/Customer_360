from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.config.settings import settings
from server.api.routes import auth_routes, agent_routes, policy_routes, customer_routes, llm_routes
from server.utils.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Enterprise-ready Customer 360 API",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_routes.router, prefix="/api/v1")
    app.include_router(agent_routes.router, prefix="/api/v1")
    app.include_router(policy_routes.router, prefix="/api/v1")
    app.include_router(customer_routes.router, prefix="/api/v1")
    app.include_router(llm_routes.router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} Server...")

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "app": settings.app_name}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
