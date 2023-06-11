"""
Create embedding with a huggingface model and tokenizer
"""

from transformers import AutoTokenizer, AutoModel


def auto_tokenizer(model_name, cache_dir=None):
    """
    Returns an transformer's AutoTokenizer from a pretrained model name.

    If cache_dir is not specified, transformer's default one will be used.

    The first time this runs, it will download the required
    model if it's not present in cache_dir.
    """
    return AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)


def auto_model(model_name, cache_dir=None):
    """
    Returns an transformer's AutoModel from a pretrained model name.

    If cache_dir is not specified, transformer's default one will be used.

    The first time this runs, it will download the required
    model if it's not present in cache_dir.
    """
    return AutoModel.from_pretrained(model_name, cache_dir=cache_dir)


def huggingface_custom(document, tokenizer, model, length=512):
    """
    Create an embedding from the provided document.

    Needs a huggingface tokenizer and model.
    To instantiate a tokenizer and a model, you can use the
    `auto_model` and `auto_tokenizer` functions in this module.
    """
    for chunk in document.text:
        inputs = tokenizer(
            chunk, padding=True, truncation=True, return_tensors="pt", max_length=length
        )
        result = model(**inputs)
        embeddings = result.last_hidden_state[:, 0, :].cpu().detach().numpy()
        lst = embeddings.flatten().tolist()
        document.embeddings.append(lst)
    return document
