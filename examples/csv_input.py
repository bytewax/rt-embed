############################
### Not Functioning Code ###
############################

from bytewax.dataflow import Dataflow

from embed.sources.file import CSVInput
from embed.stores.postgres import PGVectorOutput
from embed.embedding.huggingface import hf_document_embed
from embed.objects import Document

from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

flow = Dataflow()
flow.input("http_input", CSVInput("data/books.csv"))
# output: {"header1": "value1", "header2": "value2"}

flow.map(lambda x: Document(group_key=x['header1'], text=x['header2']))
# output: <class Document>
# class Document(BaseModel):
#     group_key: Optional[str] = 'All'
#     metadata: Optional[dict] = {}
#     text: Optional[list] = []
#     embeddings: Optional[list] = []

flow.map(lambda document: hf_document_embed(document, tokenizer, model, length=512))
# output: <class Document>

flow.output("output", PGVectorOutput(collection_name="test_collection", vector_size=512))