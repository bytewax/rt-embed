from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource
from sqlalchemy import create_engine, inspect

from embed.objects.base import Document
from embed.embedding.huggingface import hf_document_embed
from embed.stores.qdrant import QdrantOutput

from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


class SQLAlchemyInput(PartitionedInput):
    def __init__(self, connection_strings: list):
        self.urls = connection_strings

    def list_parts(self):
        # return the set of urls to be divided internally
        return set(self.connection_strings)

    def build_part(self, part_connection_string, resume_state):
        assert resume_state is None
        return _SQLAlchemySource(part_connection_string)
    
class _SQLAlchemySource(StatefulSource):
    def __init__(self, connection_string):
        engine = create_engine(connection_string)
        # create inspector
        self.inspector = inspect(engine)
        schemas = self.inspector.get_schemas_names()
        schema__tables = []
        for schema in schemas:
            table_names = self.inspector.get_table_names(schema=schema)
            for table in table_names:
                schema__tables.append((schema, table))  
        self.schema__tables = iter(schema__tables)
        
    def next(self):
        schema, table = next(self.schema__tables)
        table_representation = ""
            
        # Get columns
        columns = self.inspector.get_columns(table, schema=schema)
        table_representation + "Columns:" + " ,".join([f" - {column['name']} ({column['type']})" for column in columns])
        
        # Get foreign keys
        fks = self.inspector.get_foreign_keys(table, schema=schema)
        table_representation + "Foreign keys:" + " ,".join([f"{fk['name']}" for fk in fks])

        comments = self.inspector.get_table_comment(table, schema=schema)
        table_representation + f"{comments}"

        return {"key": f"{schema}+{table}", "schema":schema, "table_name":table, "text": table_representation}

    def snapshot(self):
        pass

    def close(self):
        pass

flow = Dataflow()
flow.input("schema_data", SQLAlchemyInput(["postgresql://user:password@localhost/mydatabase"]))
flow.map(lambda table_data: Document(key=table_data.pop("key"), text=table_data.pop("text"), metadata=table_data))
flow.map(lambda doc: hf_document_embed(doc, tokenizer, model, length=512))
flow.output("output", QdrantOutput(collection_name="test_collection", vector_size=512))