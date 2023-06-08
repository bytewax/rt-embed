try:
    import cv2
except ImportError:
    raise ValueError(
        "Could not import cv2 python package. "
        "Please install it with `pip install opencv-python`."
    )

from bytewax.inputs import (
    StatelessSource,
    StatefulSource,
    PartitionedInput,
)
from bytewax.connectors.files import DirInput


class _ImageSource(StatelessSource):
    """Image reader for image inputs.

    Uses cv2 to read the image and can
    handle the following types:
    https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56.

    Meant to be called by Input classes like
    ImgInput or DirImgInput.

    calling next returns:
    {"metadata": {"key":"value"}, "img":img}
    """

    def __init__(self, path, **cvparams):
        self._f = open(path, "rt")
        self.cvparams = cvparams

    def next(self):
        image = cv2.imread(self.path, **self.cvparams)
        assert image is not None, "file could not be read, check with os.path.exists()"
        return image


class DirImageInput(DirInput):
    """Load all images from a directory

    The directory must exist and contain identical data on all
    workers, so either run on a single machine or use a shared mount.

    Args:
        dir: Path to the directory should be a pathlib object
        glob_pat: Pattern of files to read. Defaults to "*".
    """

    def build_part(self, for_part, resume_state):
        path = self._dir / for_part
        return _ImageSource(path, resume_state)


class _HuggingfaceStreamingDatasetSource(StatefulSource):
    def __init__(self, dataset_name, split_part, batch_size):
        self.batch_size = batch_size
        if split_part not in ["train", "test", "validation"]:
            raise "Split part not available, please provide from train, test or validation"

        try:
            from datasets import load_dataset
        except ImportError:
            raise ValueError(
                "Could not import datasets python package. "
                "Please install it with `pip install datasets`."
            )
        self.dataset = load_dataset(dataset_name, split=f"{split_part}", streaming=True)

    def next(self):
        return next(iter(self.dataset))

    def snapshot(self):
        return None


class HuggingfaceDatasetStreamingInput(PartitionedInput):
    """Loads a huggingface dataset as a streaming input

    Args:
        dataset_name: name of the dataset in the huggingface hub
        split_part: string telling which part to load (test, train, validation) or combination
        batch_size: size of the batches to work on in the dataflow
    """

    def __init__(self, dataset_name: str, split_part: str):
        self.dataset_name = dataset_name
        self.split_part = split_part

    def list_parts(self):
        return {"single-part"}

    def build_part(self, for_key, resume_state):
        assert for_key == "single-part"
        assert resume_state is None
        return _HuggingfaceStreamingDatasetSource(self.dataset_name, self.split_part)


# TODO: Huggingface Dataset Source Chunks
# Should take a part of a dataset per
# worker and pass the chunk downstream

# class _HuggingfaceDatasetSource(StatefulSource):

#     def __init__(self, dataset_name, split_part, batch_size):
#         self.batch_size = batch_size
#         if split_part not in ["train", "test", "validation"]:
#             raise "Split part not available, please provide from train, test, validation or a combination"

#         try:
#             from datasets import load_dataset
#         except ImportError:
#             raise ValueError(
#                 "Could not import datasets python package. "
#                 "Please install it with `pip install datasets`."
#             )
#         self.dataset = load_dataset(dataset_name, split=f"{split_part}", streaming=True)

#     def next(self):
#         return next(iter(self.dataset))

#     def snapshot(self):
#         return None


# class HuggingfaceDatasetInput(PartitionedInput):
#     """Loads a huggingface dataset and splits it among workers
#     This should be used only with datasets that fit into memory
#     as the dataset is required to fit into memory on a single
#     machine. If the dataset is bigger than memory, use the
#     `HuggingfaceDatasetStreamingInput`

#     Args:
#         dataset_name: name of the dataset in the huggingface hub
#         split_part: string telling which part to load (test, train, validation) or combination
#         batch_size: size of the batches to work on in the dataflow

#     Next Returns:
#         dataset_chunk: a chunk of the dataset indexed as per
#     """
#     def __init__(self, dataset_name:str, split_part:str, batch_size:int):
#         self.dataset_name = dataset_name
#         self.split_part = split_part
#         self.batch_size = batch_size

#     def list_parts(self):
#         return {"single-part"}

#     def build_part(self, for_key, resume_state):
#         assert for_key == "single-part"
#         assert resume_state is None
#         return(_HuggingfaceStreamingDatasetSource(self.dataset_name, self.split_part, self.batch_size))
