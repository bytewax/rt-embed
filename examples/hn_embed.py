from bytewax.dataflow import Dataflow

from embed.sources.url import HTTPInput
from embed.processing.html import recurse_hn
from embed.embedding.huggingface import huggingface_custom, auto_tokenizer, auto_model

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

flow = Dataflow()

# Get the homepage of hackernews as the source
flow.input(
    "http_input",
    HTTPInput(
        urls=["https://news.ycombinator.com/"],
        # Set poll_frequency to None to only fetch the page once,
        # for testing.
        poll_frequency=None,
    ),
)

# The input returns a list of WebPages, so we use flat_map
# to unpack the list into single items (only one in this case)
flow.flat_map(lambda x: x)

# Now we use `recurse_hn` to extract the urls of all the entries
# in hackernews' homepage, and use flat_map again to unpack the
# list of resulting urls
flow.flat_map(lambda x: recurse_hn(x.html))

# embed's WebPage object allows us to tokenize the html content
# using a tokenizer from transformer's library
flow.map(lambda x: x.parse_html(auto_tokenizer(MODEL_NAME)))

# We need to initialize a new tokenizer here, since this could
# run in parallel with the other one thanks to bytewax, and we
# can only use an instance at a time
flow.map(
    lambda x: huggingface_custom(
        x, auto_tokenizer(MODEL_NAME), auto_model(MODEL_NAME), length=512
    )
)

# Finally send the embeddings to qdrant
# from embed.stores.qdrant import QdrantOutput
# flow.output("output", QdrantOutput(collection_name="test_collection", vector_size=512))

# This is a stdout output for testing without qdrant
from bytewax.connectors.stdio import StdOutput

flow.map(lambda x: f"Processed: {x}")
flow.output("output", StdOutput())
