from unstructured.staging.huggingface import chunk_by_attention_window

# chunk the news article and summary
def chunk(text, tokenizer):
    chunks = []
    for chunk in text:
        chunks += chunk_by_attention_window(text, tokenizer)

    return chunks
