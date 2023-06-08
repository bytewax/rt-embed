from embed import Pipeline

pl = Pipeline(model_name="sentence-transformers/all-MiniLM-L6-v2")
pl.hacker_news(poll_frequency=None)
pl.parse_html()
pl.embed_document()
pl.qdrant_output(collection="test_collection", vector_size=384)
pl.run(workers=8)
