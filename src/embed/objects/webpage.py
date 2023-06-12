import time
import requests
import hashlib

from typing import Optional

from .base import Document

from fake_useragent import UserAgent
from requests.exceptions import RequestException
from unstructured.partition.html import partition_html
from unstructured.cleaners.core import (
    clean,
    replace_unicode_quotes,
    clean_non_ascii_chars,
)
from unstructured.staging.huggingface import chunk_by_attention_window


class WebPage(Document):
    url: str
    html: Optional[str]
    content: Optional[str]
    headers: Optional[dict] = None
    max_retries: int = 3
    wait_time: int = 1

    def __str__(self):
        return f"WebPage({self.url})"

    def get_page(self):
        if self.headers is None:
            # make a user agent
            ua = UserAgent()

            self.headers = {
                "User-Agent": ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*"
                ";q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referrer": "https://www.google.com/",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

        # Send the initial request
        for i in range(self.max_retries):
            try:
                response = requests.get(self.url, headers=self.headers)
                response.raise_for_status()
                self.html = response.content
                break
            except RequestException as e:
                print(f"Request failed (attempt {i + 1}/{self.max_retries}): {e}")
                if i == self.max_retries:
                    print(f"skipping url {self.url}")
                    self.html = ""
                    break
                print(f"Retrying in {self.wait_time} seconds...")
                time.sleep(self.wait_time)
                i += 1

    # Clean the code and setup the dataclass
    def parse_html(self, tokenizer):
        elements = partition_html(text=self.html)
        elements = [x for x in elements if x.to_dict()["type"] == "NarrativeText"]
        elements = " ".join([f"{x}" for x in elements])
        self.content = clean_non_ascii_chars(replace_unicode_quotes(clean(elements)))
        self.text += chunk_by_attention_window(self.content, tokenizer)
        try:
            self.group_key = hashlib.md5(self.content[:2000].encode()).hexdigest()
        except AttributeError:
            self.group_key = hashlib.md5(self.content[:2000]).hexdigest()

        return self
