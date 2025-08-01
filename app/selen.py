import os
import logging
from distutils.util import strtobool
from app.utils import (
    fix_header,
    get_host_referer,
)
from selenium import webdriver

# Configuration
CONF_OPTS = ('TIMEOUT', 'USERAGENT', 'PARTIAL_RESPONSE', )
TIMEOUT = os.environ.get('TIMEOUT') or 10000
USERAGENT = os.environ.get('USERAGENT') or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15"
PARTIAL_RESPONSE = os.environ.get('PARTIAL_RESPONSE') or 'true'

BROWSER_BUSY = False

logger = logging.getLogger("uvicorn.error")
# logging.getLogger("playwright").setLevel(logging.DEBUG)

logger.info('Configs:')
for opt in CONF_OPTS:
    logger.info(f'{opt}: {eval(opt)}')

class Epiphany(webdriver.Remote):
    def __init__(self, url):
        options = webdriver.WebKitGTKOptions()
        options.binary_location = '/usr/bin/epiphany'
        options.overlay_scrollbars_enabled = False
        options.add_argument('--automation-mode')
        # options.set_capability('browserName', 'Epiphany')
        # options.set_capability('browserVersion', '3.36.4')
        # options.set_capability('browserVersion', 'ANY')
        # options.set_capability('version', '3.36.4')
        # options.set_capability('version', 'ANY')
        capabilities = options.to_capabilities()
        print(capabilities)
        webdriver.Remote.__init__(self, command_executor=url, options=options, desired_capabilities=capabilities)

def browser_busy():
    return BROWSER_BUSY

def fetch(url, proxy, ua, timeout, partial):
    """
    Main function for getting webpage content
    """
    global BROWSER_BUSY
    # if proxy:
    #     context_opts = {**context_opts, 'proxy': {'server': proxy}}
    # partial_response = strtobool(partial or PARTIAL_RESPONSE)
    user_agent = ua or USERAGENT
    host, referer = get_host_referer(url)
    selen_headers = {
        'selen-proxy': proxy or 'no_proxy',
        'selen-user-agent': user_agent,
        'selen-timeout': str(timeout or TIMEOUT),
    }
    try:
        BROWSER_BUSY = True
        # TODO improve this
        browser = Epiphany('127.0.0.1:4444')
        browser.get(url)
        content = browser.page_source
        headers = selen_headers
        status = 200
        browser.quit()
    except Exception as e:
        raise e
    finally:
        BROWSER_BUSY = False
    return status, headers, content