import os

from starlette.templating import Jinja2Templates

from app.config import ROOT_PATH

templates = Jinja2Templates(directory=os.path.join(ROOT_PATH, "templates"))
