"""
Batching Methods
"""

from bytewax.dataflow import Dataflow  # noqa: F401


def func(self, other_func):
    other_func(self)


Dataflow.subflow = func

__all__ = [
    "Dataflow",
]
