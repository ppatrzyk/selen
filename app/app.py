import logging

from starlette.applications import Starlette
from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    Response,
)
from starlette.routing import Route

from app.utils import validate_url

logger = logging.getLogger("uvicorn.error")

RENDER_PARAMS = ('url', 'proxy', 'ua', 'timeout', 'partial')

def render(request):
    """
    /render endpoint
    Parameters:
      - url (required) - page to fetch
      - proxy (required if PROXY_ENABLED=true) - proxy address
      - ua - custom user agent
      - timeout - in ms
      - partial - whether to return partial on timeout
    """
    # TODO implement
    return PlainTextResponse("OK", status_code=200)

def healthcheck(request):
    """
    /healthcheck Endpoint
    Indicates if current browser works
    """
    return PlainTextResponse("OK", status_code=200)

routes = (
    Route("/healthcheck", endpoint=healthcheck, methods=("GET", )),
    Route("/render", endpoint=render, methods=("GET", "POST")),
)

app = Starlette(routes=routes)
