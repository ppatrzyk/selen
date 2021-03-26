import logging

from starlette.applications import Starlette
from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    Response,
)
from starlette.routing import Route

from app.selen import browser_busy, fetch
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
    if request.method == 'GET':
        raw_params = request.query_params
    elif request.method == 'POST':
        raw_params = request.json()
    else:
        raise AssertionError('should never happen')
    params = {key.lower(): val for key, val in raw_params.items()}
    logger.debug(request.headers)
    logger.debug(params)
    fetch_params = {key: params.get(key) for key in RENDER_PARAMS}
    try:
        url = fetch_params.get('url')
        assert url, 'No URL provided'
        assert validate_url(url), f'Invalid url: {url}'
    except Exception as e:
        return PlainTextResponse(str(e), status_code=422)
    try:
        assert not browser_busy(), 'browser busy'
    except Exception as e:
        return PlainTextResponse(str(e), status_code=429)
    try:
        status, headers, content = fetch(**fetch_params)
        content_type = headers.get('content-type') or 'text/plain'
        logger.debug(headers)
        response = Response(
            content=content,
            status_code=status,
            headers=headers,
            media_type=content_type
        )
        return response
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

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
