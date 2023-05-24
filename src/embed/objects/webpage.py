import time
import hashlib

from fake_useragent import UserAgent
import requests
from requests.exceptions import RequestException

from embed.objects.base import Document

from unstructured.partition.html import partition_html
from unstructured.cleaners.core import (
    clean,
    replace_unicode_quotes,
    clean_non_ascii_chars,
)
from unstructured.staging.huggingface import chunk_by_attention_window
from unstructured.staging.huggingface import stage_for_transformers

from typing import Any, Optional


class WebPage(Document):
    url: str
    html: Optional[str]
    content: Optional[str]
    headers: Optional[dict] = {}
    max_retries: Optional[int] = 3
    wait_time: Optional[int] = 1

    def __str__(self):
        return f"WebPage: url={self.url}, html={self.html}, text={self.text}, metadata={self.metadata}"

    def get_page(self):
        if self.headers == {}:
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
        current_wait_time = self.wait_time
        # Send the initial request
        for i in range(self.max_retries + 1):
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
                print(f"Retrying in {current_wait_time} seconds...")
                time.sleep(current_wait_time)
                i += 1

    # Clean the code and setup the dataclass
    def parse_html(self, tokenizer):
        article_elements = partition_html(text=self.html)
        self.content = clean_non_ascii_chars(
            replace_unicode_quotes(
                clean(
                    " ".join(
                        [
                            str(x) if x.to_dict()["type"] == "NarrativeText" else ""
                            for x in article_elements
                        ]
                    )
                )
            )
        )
        self.text += chunk_by_attention_window(self.content, tokenizer)
        try:
            self.group_key = hashlib.md5(self.content[:2000].encode()).hexdigest()
        except AttributeError:
            self.group_key = hashlib.md5(self.content[:2000]).hexdigest()

        return self
