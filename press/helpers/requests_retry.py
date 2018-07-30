import requests

from requests.adapters import HTTPAdapter
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.util.retry import Retry


# {backoff factor} * (2 ^ ({number of total retries} - 1))
# 0.3 * 2^13 = 2457 (~3600 = 60 mins)

def requests_retry_session(
    retries=13, backoff_factor=0.3, status_forcelist=(500, 502, 504),
    session=None
):
    session = session or requests.Session()
    retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
