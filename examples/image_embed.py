import torch
import torchvision.transforms as T

from embed import Pipeline

from transformers import AutoFeatureExtractor

MODEL_NAME = "nateraw/vit-base-beans"
EXTRACTOR = AutoFeatureExtractor.from_pretrained(MODEL_NAME)

# Data transformation chain.
TRANSFORM_CHAIN = T.Compose(
    [
        # We first resize the input image to 256x256 and then we take center crop.
        T.Resize(int((256 / 224) * EXTRACTOR.size["height"])),
        T.CenterCrop(EXTRACTOR.size["height"]),
        T.ToTensor(),
        T.Normalize(mean=EXTRACTOR.image_mean, std=EXTRACTOR.image_std),
    ]
)

# Here, we map embedding extraction utility on our subset of candidate images.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

pl = Pipeline(MODEL_NAME)
pl.huggingface_input("beans", "train")
pl.batch(length=10)
pl.embed_image(DEVICE, TRANSFORM_CHAIN)
pl.sqlite_vector_output()
