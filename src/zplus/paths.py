"""Access to bundled package data (templates, overrides, seed manifest)."""
from importlib.resources import files


def data_root():
    """Traversable for the packaged `zplus/data` directory."""
    return files("zplus") / "data"


def read_data(*parts):
    """Return the bytes of a bundled data file, e.g. read_data('env.example')."""
    node = data_root()
    for p in parts:
        node = node / p
    return node.read_bytes()
