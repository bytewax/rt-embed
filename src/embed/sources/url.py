from datetime import datetime

from bytewax.inputs import DynamicInput, StatelessSource

from embed.objects import WebPage


class HTTPSource(StatelessSource):
    def __init__(self, urls, poll_frequency, max_retries=3, wait_time=1):
        self.urls = urls
        self.poll_frequency = poll_frequency
        self.max_retries = max_retries
        self.wait_time = wait_time
        self.poll_time = datetime.now()
        self.counter = 0

    def next(self):
        elapsed_time = datetime.now() - self.poll_time
        if self.counter > 0 and elapsed_time.total_seconds() < self.poll_frequency:
            return None
        else:
            start_req = datetime.now()
            webpages = []
            for url in self.urls:
                wp = WebPage(
                    url=url, max_retries=self.max_retries, wait_time=self.wait_time
                )
                wp.get_page()
                webpages.append(wp)

            total_req = start_req - datetime.now()
            self.poll_frequency = self.poll_frequency - total_req.total_seconds()
            self.poll_time = datetime.now()
            self.counter += 1
            return webpages


class HTTPInput(DynamicInput):
    """Given a set of urls retrieve the html content from each url"""

    def __init__(self, urls, poll_frequency=600, max_retries=3, wait_time=1):
        self.urls = urls
        self.poll_frequency = poll_frequency
        self.max_retries = max_retries
        self.wait_time = wait_time

    def build(self, worker_index, worker_count):
        urls_per_worker = int(len(self.urls) / worker_count)
        worker_urls = self.urls[
            int(worker_index * urls_per_worker) : int(
                worker_index * urls_per_worker + urls_per_worker
            )
        ]
        return HTTPSource(
            worker_urls,
            self.poll_frequency,
            max_retries=self.max_retries,
            wait_time=self.wait_time,
        )
