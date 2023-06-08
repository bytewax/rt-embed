"""
Pipeline
"""

from .embedding.huggingface import hf_document_embed
from .embedding.huggingface import hf_image_embed
from .objects import Document
from .processing.html import recurse_hn
from .sources.file import HuggingfaceDatasetStreamingInput
from .sources.url import HTTPInput
from .stores.qdrant import QdrantOutput

# from .stores.postgres import PGVectorOutput
# from .stores.sqlite import SqliteVectorOutput

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.run import cli_main

from transformers import AutoTokenizer, AutoModel


class Pipeline(Dataflow):
    """
    A custom dataflow tailored for real time embeddings pipelines.
    """

    ##
    # Initialization stuff, bytewax related
    ##
    def __new__(cls, *args, **kwargs):
        # We don't want to pass model_name to __new__
        return Dataflow.__new__(cls)

    def __init__(self, model_name=None):
        super().__init__()
        self.model_name = model_name
        if self.model_name is not None:
            # Preload models
            AutoModel.from_pretrained(model_name)
            AutoTokenizer.from_pretrained(model_name)

    def _check_model_name(self):
        if self.model_name is None:
            raise RuntimeError(
                "Initialize the Pipeline with a model name to use transformers"
            )

    def run(self, workers=1):
        cli_main(self, processes=None, workers_per_process=workers, process_id=0)

    def get_model(self):
        """
        TODO
        """
        self._check_model_name()
        return AutoModel.from_pretrained(self.model_name)

    def get_tokenizer(self):
        """
        TODO
        """
        self._check_model_name()
        return AutoTokenizer.from_pretrained(self.model_name)

    ##
    # Inputs
    ##
    def http_input(self, urls, poll_frequency=300):
        """
        Periodically fetch the provided urls, and emits Documents.
        """
        self.input(
            "http_input",
            HTTPInput(urls=urls, poll_frequency=poll_frequency, max_retries=1),
        )
        self.flat_map(lambda x: x)
        return self

    def hacker_news(self, poll_frequency=300):
        """
        Parse hackernews homepage, emits Documents with the linked urls content.
        """
        self.http_input(
            urls=["https://news.ycombinator.com/"], poll_frequency=poll_frequency
        )
        self.recurse_hn()
        return self

    def huggingface_input(self, dataset_name, split_part):
        """
        TODO
        """
        self.input(
            "huggingface-input",
            HuggingfaceDatasetStreamingInput(dataset_name, split_part),
        )

    ##
    # Processing
    ##
    def parse_html(self):
        """
        TODO
        """
        self.map(lambda x: x.parse_html(self.get_tokenizer()))
        return self

    def embed_document(self):
        """
        TODO
        """
        self.map(
            lambda x: hf_document_embed(
                x, self.get_tokenizer(), self.get_model(), length=512
            )
        )
        return self

    def embed_image(self, device, transformation_chain):
        self.map(
            lambda x: hf_image_embed(
                x, self.get_model().to(device), transformation_chain, device
            )
        )
        return self

    def recurse_hn(self):
        """
        TODO
        """
        self.flat_map(lambda x: recurse_hn(x.html))

        def fetch(page):
            page.get_page()
            if page.html:
                return page
            else:
                return None

        self.filter_map(fetch)
        self.redistribute()
        return self

    def make_document(self, group_key=None, metadata=None, text=None, embeddings=None):
        """
        Takes a `metadata` dict, and builds a Document.
        """
        self.map(lambda x: Document(group_key=x[group_key], text=x[text], metadata=x))
        return self

    ##
    # Outputs
    ##
    def qdrant_output(self, collection, vector_size):
        """
        TODO
        """
        self.output(
            "qdrant-output",
            QdrantOutput(collection_name=collection, vector_size=vector_size),
        )
        return self

    def stdout(self):
        """
        TODO
        """
        self.output("std-output", StdOutput())
        return self

    # def pg_vector_output(self, collection, vector_size):
    #     self.output(
    #         "pgvector-output",
    #         PGVectorOutput(collection_name=collection, vector_size=vector_size),
    #     )

    # def sqlite_vector_output(self):
    #     self.output(
    #         "sqlite-output",
    #         SQLiteVectorOutput()
    #     )


__all__ = ["Pipeline"]
