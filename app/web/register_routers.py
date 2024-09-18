from fastapi import FastAPI

from app.web.routers import webhooks


def register_fastapi_routers(app: FastAPI) -> None:
    app.include_router(webhooks.router)
