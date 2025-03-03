import random
import time
from fake_useragent import UserAgent


class RandomUserAgentMiddleware(object):
    def __init__(self):
        self.ua = UserAgent()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random


class RetryMiddleware(object):
    def __init__(self):
        self.retry_delay = 3
        self.retry_http_codes = {403}

    def process_response(self, request, response, spider):
        """If the response is a 403, sleep for a period and then retry the request."""
        if response.status == 403:
            time.sleep(self.retry_delay + random.uniform(1, 5))
            spider.logger.warning(f"403 Forbidden response encountered, sleep for retrying")
        return response



