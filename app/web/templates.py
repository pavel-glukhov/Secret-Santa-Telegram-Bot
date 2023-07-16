import os

from starlette.templating import Jinja2Templates

from app.config import ROOT_PATH


def template(root_path=ROOT_PATH) -> Jinja2Templates:
    jinja_template = Jinja2Templates(
        directory=os.path.join(root_path, "templates")
    )
    return jinja_template
