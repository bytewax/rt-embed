# create embedding and store in vector db
def embedding(document, tokenizer, model):
    '''
    Create an embedding from the provided document
    '''
    for chunk in document.text:
        inputs = tokenizer(chunk, padding=True, truncation=True, return_tensors="pt", max_length=512)
        result = model(**inputs)
        embeddings = result.last_hidden_state[:, 0, :].cpu().detach().numpy()
        lst = embeddings.flatten().tolist()
        document.embeddings.append(lst)
    return document