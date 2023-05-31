############################
### Not Functioning Code ###
############################

from bytewax.dataflow import Dataflow

from embed.sources.file import HuggingfaceDatasetStreamingInput
from embed.embedding.huggingface import hf_image_embed
from embed.objects.base import Image
from embed.stores.sqlite import SQLiteVectorOutput

from transformers import AutoFeatureExtractor, AutoModel
import torch

model_ckpt = "nateraw/vit-base-beans"
extractor = AutoFeatureExtractor.from_pretrained(model_ckpt)
model = AutoModel.from_pretrained(model_ckpt)
hidden_dim = model.config.hidden_size

flow = Dataflow()
flow.input("input", HuggingfaceDatasetStreamingInput("beans", "train"))
#[{"path":"path/to/image", "image":<Image Object>}]

flow.batch(length=10) # not implemented, would be a reduce subflow
#[<embed.Image Class>, <embed.Image Class>, ...]

# # Transform images
import torchvision.transforms as T


# Data transformation chain.
transformation_chain = T.Compose(
    [
        # We first resize the input image to 256x256 and then we take center crop.
        T.Resize(int((256 / 224) * extractor.size["height"])),
        T.CenterCrop(extractor.size["height"]),
        T.ToTensor(),
        T.Normalize(mean=extractor.image_mean, std=extractor.image_std),
    ]
)

# Here, we map embedding extraction utility on our subset of candidate images.
device = "cuda" if torch.cuda.is_available() else "cpu"

flow.map(lambda x: hf_image_embed(x, model.to(device), transformation_chain, device))
# [<Image Class>, <Image Class>] # including vectors

flow.output("out", SQLiteVectorOutput())