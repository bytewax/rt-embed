from embed.objects import Document, Image

def process_inputs(inputs, model, device):
    """
    Process inputs and get embeddings
    """
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0].cpu().detach().numpy()
    return embeddings.flatten().tolist()

def get_document_inputs(chunk, tokenizer, length=512):
    """
    Get document model inputs
    """
    return tokenizer(chunk, padding=True, truncation=True, return_tensors="pt", max_length=length)

def get_image_inputs(batch, transformation_chain, device):
    """
    Get image model inputs
    """
    images = [image_data['image'] for image_data in batch]
    image_batch_transformed = torch.stack(
        [transformation_chain(image) for image in images]
    )
    return {"pixel_values": image_batch_transformed.to(device)}

def hf_document_embed(document:Document, tokenizer, model, length=512):
    """
    Create an embedding from the provided document
    """
    for chunk in document.text:
        inputs = get_document_inputs(chunk, tokenizer, length)
        embeddings = process_inputs(inputs, model)
        document.embeddings.append(embeddings)
    return document

def hf_image_embed(batch:list, model, transformation_chain, device):
    inputs = get_image_inputs(batch, transformation_chain)
    embeddings = process_inputs(inputs, model, device)
    return {"embeddings": embeddings}
