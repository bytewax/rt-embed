from embed import Pipeline

pl = Pipeline(model_name="sentence-transformers/all-MiniLM-L6-v2")
pl.csv_input("data/books.csv")
pl.make_document(group_key="header1", text="header2")
pl.embed_document()
# pl.pg_vector_output("test_collection", vector_size=512)
pl.stdout()
pl.run()
