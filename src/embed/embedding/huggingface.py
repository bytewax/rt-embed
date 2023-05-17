# create embedding with a huggingface model
def huggingface_custom(document, tokenizer, model, length=512):
    '''
    Create an embedding from the provided document
    '''
    for chunk in document.text:
        inputs = tokenizer(chunk, padding=True, truncation=True, return_tensors="pt", max_length=length)
        result = model(**inputs)
        embeddings = result.last_hidden_state[:, 0, :].cpu().detach().numpy()
        lst = embeddings.flatten().tolist()
        document.embeddings.append(lst)
    return document