import os
import re
import logging
import io
import numpy as np

from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource
from bytewax.connectors.stdio import StdOutput
import whisper
from pytube import YouTube, request
from pydub import AudioSegment

import torch

logging.basicConfig(level=logging.INFO)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base")
print(DEVICE)


class YouTubeInput(PartitionedInput):
    def __init__(self, urls: list, audio_only: bool = True):
        self.urls = urls
        self.audio_only = audio_only

    def list_parts(self):
        # return the set of urls to be divided internally
        return set(self.urls)

    def build_part(self, part_url, resume_state):
        assert resume_state is None
        return _YouTubeSource(part_url, self.audio_only)


class _YouTubeSource(StatefulSource):
    def __init__(self, yt_url, audio_only):
        # TODO: check for ffmpeg
        self.complete = False
        self.yt_url = yt_url
        self.yt = YouTube(self.yt_url, on_complete_callback=self.mark_complete)
        if audio_only:
            self.stream = self.yt.streams.filter(only_audio=True).first()
        else:
            self.stream = self.yt.streams.filter().first()
        self.audio_file = self.stream.download(
            filename=f"{self.yt_url.split('?')[-1]}.mp4"
        )

    def mark_complete(self, file_path, x):
        self.complete = True
        self.processed = False

    def next(self):
        if not self.complete:
            return None
        elif self.processed:
            raise StopIteration
        else:
            self.processed = True
            return self.audio_file
        # chunk = next(self.audio_stream)
        # self.bytes_remaining -= len(chunk)
        # byte_io = io.BytesIO(chunk)
        # audio_segment = AudioSegment.from_file(byte_io, format=self.format)
        # samples = np.array(audio_segment.get_array_of_samples()).T.astype(np.float32)

    def snapshot(self):
        pass

    def close(self):
        os.remove(self.audio_file)


flow = Dataflow()
flow.input("youtube", YouTubeInput(["https://www.youtube.com/watch?v=qJ3PWyx7w2Q"]))
flow.map(model.transcribe)
flow.output("out", StdOutput())
