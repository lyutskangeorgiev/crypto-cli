import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

def build_session(config) -> "requests.Session":
    s = requests.Session()

    headers = {"x-cg-demo-api-key": config.api_key,
               "User-Agent": config.user_agent,
               "Accept": "application/json"}

    s.headers.update(headers)
    retry = Retry(connect=3,  backoff_factor=0.5,
                  #how long to wait between retries
                  #Retry 1: 0.5 * 2**0 = 0.5s
                  #Retry 2: 0.5 * 2**1 = 1.0s
                  #Retry 3: 0.5 * 2**2 = 2.0s
                  status_forcelist=[429, 500, 502, 503, 504],
                  #HTTP response codes that trigger a retry
                  #excludes not connection errors (4xx...)
                  allowed_methods={"GET"}
                  )
    adapter = HTTPAdapter(max_retries=retry)
    # MOUNTING (important):
    #This scopes our retry policy to the CoinGecko host only.
    #(Longest-prefix wins: this beats the generic "https://" adapter.)
    s.mount("https://api.coingecko.com/", adapter)
    return s