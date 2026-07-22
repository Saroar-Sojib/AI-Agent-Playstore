import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import app.infrastructure.audit_events  # noqa     # timestamps: create_uid/write_uid

from app.core.dependencies import set_user_context
from app.core.config import settings
from app.core.agent_middleware import AgentMiddleware
from app.infrastructure.database import engine
from app.infrastructure.redis import create_redis_client
from app.modules.users.api.v1.router import router as users_router
from app.modules.agents.api.v1.router import router as agents_router
from app.modules.auth.api.v1.router import router as auth_router
from app.modules.chat.api.v1.router import router as chat_router
from app.core.exception_handlers import register_exception_handlers

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    dependencies=[Depends(set_user_context)],
)

# Agent middleware must run BEFORE CORS so context is set for all handlers
app.add_middleware(AgentMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(users_router)
app.include_router(chat_router)


register_exception_handlers(app)


@app.on_event("startup")
async def _connect_redis() -> None:
    app.state.redis = create_redis_client()


@app.on_event("shutdown")
async def _dispose_engine() -> None:
    await engine.dispose()
    redis_client = getattr(app.state, "redis", None)
    if redis_client is not None:
        await redis_client.aclose()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version="1.0.0", routes=app.routes)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
