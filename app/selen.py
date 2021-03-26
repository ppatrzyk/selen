import os
import logging
from distutils.util import strtobool
from app.utils import (
    fix_header,
    get_host_referer,
)
from selenium import webdriver

# Configuration
CONF_OPTS = ('PROXY_ENABLED', 'TIMEOUT', 'USERAGENT', 'PARTIAL_RESPONSE', )
PROXY_ENABLED = strtobool(os.environ.get('PROXY_ENABLED') or 'false')
TIMEOUT = os.environ.get('TIMEOUT') or 10000
USERAGENT = os.environ.get('USERAGENT') or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15"
PARTIAL_RESPONSE = os.environ.get('PARTIAL_RESPONSE') or 'true'

# https://playwright.dev/python/docs/api/class-request#requestresource_type
REQUEST_OK = ('document', 'script', 'fetch', 'xhr', )
# TODO preserve these from original response somehow?
TRASH_HEADER = ('content-length', 'content-encoding', 'server', 'date', )
EMPTY_PAGE = '<html><head></head><body></body></html>'
BROWSER_BUSY = False

logger = logging.getLogger("uvicorn.error")
# logging.getLogger("playwright").setLevel(logging.DEBUG)

logger.info('Configs:')
for opt in CONF_OPTS:
    logger.info(f'{opt}: {eval(opt)}')

class Epiphany(webdriver.WebKitGTK):
    def __init__(self):
        options = webdriver.WebKitGTKOptions()
        options.binary_location = 'epiphany'
        options.add_argument('--automation-mode')
        options.add_argument('--display=:19')
        options.set_capability('browserName', 'Epiphany')
        options.set_capability('version', '3.36.4')

        webdriver.WebKitGTK.__init__(self, options=options, desired_capabilities={})

ephy = Epiphany()
ephy.get('http://www.patrzyk.me/foreign-tourists')
print(ephy.page_source)
ephy.quit()

def browser_busy():
    return BROWSER_BUSY

def process_request(route):
    """
    Rejects unnecessary requests for e.g. images
    """
    # TODO some filters from adblocks?
    res_type = route.request.resource_type
    url = route.request.url
    logger.debug(f'{res_type}: {url}')
    if res_type in REQUEST_OK:
        route.continue_()
    else:
        route.abort()

def fetch(url, proxy, ua, timeout, partial):
    """
    Main function for getting webpage content
    """
    global BROWSER_BUSY
    if PROXY_ENABLED:
        assert proxy, 'PROXY_ENABLED=true but no proxy parameter provided'
        context_opts = {**context_opts, 'proxy': {'server': proxy}}
    partial_response = strtobool(partial or PARTIAL_RESPONSE)
    user_agent = ua or USERAGENT
    host, referer = get_host_referer(url)
    goto_params = {
        'url': url,
        'referer': referer,
        'timeout': int(timeout or TIMEOUT),
        'wait_until': 'networkidle'
    }
    context_opts = {
        'ignore_https_errors': True,
        'locale': 'en-US',
        'user_agent': user_agent,
        'extra_http_headers': {'host': host, 'referer': referer},
        # https://playwright.dev/python/docs/api/class-browser#browsernew_contextkwargs
    }
    wraas_headers = {
        'wraas-proxy': proxy or 'no_proxy',
        'wraas-user-agent': user_agent,
        'wraas-timeout': str(timeout or TIMEOUT),
    }
    try:
        BROWSER_BUSY = True
        with sync_playwright() as p:
            browser_opts = {}
            if PROXY_ENABLED:
                browser_opts['proxy'] = {'server': 'any-proxy'}
            browser = p.firefox.launch(**browser_opts)
            context = browser.new_context(**context_opts)
            context.route("*", process_request)
            page = context.new_page()
            try:
                response = page.goto(**goto_params)
                content = page.content()
            except Exception as e:
                logger.debug('goto failed (timeout)')
                if not partial_response:
                    raise e
                content = page.content()
                if content == EMPTY_PAGE:
                    logger.debug('partial enabled but page is empty')
                    raise e
                logger.debug('partial html exists')
                status = 200
                headers = {
                    **wraas_headers,
                    'wraas-partial': 'true',
                    'content-type': 'text/html',
                }
            else:
                status = response.status
                headers = {
                    **wraas_headers,
                    'wraas-partial': 'false',
                    **{k:fix_header(v) for k,v in response.headers.items() if k not in TRASH_HEADER},
                }
            context.close()
    except Exception as e:
        raise e
    finally:
        BROWSER_BUSY = False
    return status, headers, content