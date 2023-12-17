import os

from starlette.datastructures import URL
from starlette.templating import Jinja2Templates

from app.config import ROOT_PATH


def template(root_path=ROOT_PATH) -> Jinja2Templates:
    jinja_template = Jinja2Templates(
        directory=os.path.join(root_path, "templates")
    )
    jinja_template.env.globals['URL'] = URL
    return jinja_template
