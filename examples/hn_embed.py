from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutput

from embed.sources.url import HTTPInput
from embed.processing.html import recurse_hn
from embed.embedding.huggingface import hf_document_embed
from embed.stores.qdrant import QdrantOutput

from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

flow = Dataflow()
flow.input(
    "http_input", HTTPInput(urls=["https://news.ycombinator.com/"], poll_frequency=300)
)
flow.flat_map(lambda x: x)
flow.flat_map(lambda x: recurse_hn(x.html))

# TODO - Deduplication

flow.map(lambda x: x.parse_html(tokenizer))

flow.map(lambda x: hf_document_embed(x, tokenizer, model, length=512))
flow.output("output", QdrantOutput(collection_name="test_collection", vector_size=512))
