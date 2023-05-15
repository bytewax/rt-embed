# rt-embed

RT-Embed is a composable pipeline utility for creating scalable and efficient embedding pipelines from various real-time data sources. 

## Overview

An embedding is a representation of something as a vector - language, images, sequences of events can all be represented as vectors. Calculating an embedding has become prominent with the increase in popularity of large language models as a way to retrieve information for the language model to present to the user based on a query. The process involves ingesting data, preparing it and then computing the embeddings before writing them to a database capable of vector search.

Most of the current solutions for creating embeddings are either very opinionated and one-size-fits all, brittle wrappers over the entire ecosystem or they don't cater to data that isn't static.

RT Embed is an effort to make a best in class pipeline utility that will make it straightforward to make composable pipelines with different data inputs and storage layers. RT Embed is focused on managing data that changes over time.

Why do we care about data that isn't static and changes over time? Simply put, the world is always updating around us and the need to retrieve the most recent data is pertinent to having an understanding of the world. To illustrate this, imagine if google didn't continuously scrape webpages to provide an up to date search result. The search wouldn't be very relevant.

RT Embed is built on top of Bytewax, a Python dataflow based processor. Bytewax has the concept of state so we can use it to extend our embedding possibilities to streaming sources. Bytewax is also capable of scaling from a single main process to many processes making it easy to run locally and scale as needed without changing code.

## Overview

An RT embed pipeline is made up of at least 3 parts. An input source, the computation of the embedding and an output store.

Define an input source

```python
from rt-embed.sources import HTTPInput

flow = Dataflow()
flow.input(HTTPInput(urls=["https://news.ycombinator.com/"], poll_frequency=300))
```

Select a processor or write your own

```python
from rt-embed.processors import recurse_hn

flow.map(lambda x: recurse_hn)
```

Select an embedding model or create your own

```python
from rt-embed.embedding import huggingface

from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

flow.map(huggingface(tokenizer, model))
```

Define an output store

```python
from rt-embed.stores import QdrantVectorOutput

flow.output("output", QdrantVectorOutput(collection_name="test_collection", vector_size=512))
```

Start the vector store

```shell
docker run -p 6333:6333 qdrant/qdrant
```

Run it

```shell
python pipeline.py
```
