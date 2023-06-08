from time import time

from bytewax.inputs import DynamicInput, StatelessSource

from ..objects import WebPage


class HTTPSource(StatelessSource):
    def __init__(self, urls, poll_frequency, max_retries=3, wait_time=1):
        self.urls = urls
        self.poll_frequency = poll_frequency
        self.max_retries = max_retries
        self.wait_time = wait_time
        self.poll_time = None

    def next(self):
        # If self.poll_time is not None, we have polled at least once.
        if self.poll_time is not None:
            # If self.poll_frequency is None, we stop polling
            if self.poll_frequency is None:
                raise StopIteration
            # Otherwise we wait for the given amount of seconds
            # to pass before fetching the page again, and return
            # None meanwhile.
            elif time() - self.poll_time < self.poll_frequency:
                return None

        self.poll_time = time()
        webpages = []
        for url in self.urls:
            page = WebPage(
                url=url, max_retries=self.max_retries, wait_time=self.wait_time
            )
            page.get_page()
            webpages.append(page)
        return webpages


class HTTPInput(DynamicInput):
    """Given a set of urls retrieve the html content from each url"""

    def __init__(self, urls, poll_frequency=600, max_retries=3, wait_time=1):
        self.urls = urls
        self.poll_frequency = poll_frequency
        self.max_retries = max_retries
        self.wait_time = wait_time

    def build(self, worker_index, worker_count):
        urls_per_worker = max(1, int(len(self.urls) / worker_count))
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
