
import re
from urllib.parse import urlparse

def fix_header(header):
    """
    Headers returned by Playwright are displayed invalid (?)
    """
    return re.sub('\n', '', header)

def validate_url(url):
    """
    Simple url validator
    """
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(re.search('\.', parsed.netloc))

def get_host_referer(url):
    """
    Set host and referer to the website being fetched
    """
    parsed = urlparse(url.lower())
    try:
        host = parsed.netloc
        referer = parsed._replace(path='').geturl()
    except:
        host = 'www.duckduckgo.com'
        referer = "https://duckduckgo.com/"
    return host, referer
