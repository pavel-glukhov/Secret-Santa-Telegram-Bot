import os

from fastapi import FastAPI
from app.web.routers import auth, users, general
from fastapi.staticfiles import StaticFiles

from app.web.exceptions.app_exceptions import (
    NotAuthenticatedException,
    NotAccessException,
    PageNotFoundException,
    InternalErrorException,
    not_authenticated,
    internal_error,
    not_found_error,
    access_denied
)
from app.config import root_path

app = FastAPI(debug=True)
app.mount("/static", StaticFiles(directory=os.path.join(root_path, "static")),
          name="static")

app.include_router(general.router)
app.include_router(users.router)
app.include_router(auth.router)

app.add_exception_handler(NotAuthenticatedException, not_authenticated)
app.add_exception_handler(NotAccessException, access_denied)
app.add_exception_handler(PageNotFoundException, not_found_error)
app.add_exception_handler(InternalErrorException, internal_error)
