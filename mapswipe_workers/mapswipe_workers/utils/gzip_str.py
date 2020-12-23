import base64
import gzip
import io
import json
from typing import Dict, List


def gzip_str(string_: str) -> bytes:
    """Produce a complete gzip-compatible binary string."""
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())

    bytes_obj = out.getvalue()
    return bytes_obj


def gunzip_bytes_obj(bytes_obj: bytes) -> str:
    """Decompress gzip-compatible binary string."""
    return gzip.decompress(bytes_obj).decode()


def compress_tasks(tasks_list: List[Dict]) -> str:
    """Compress tasks for footprint project type using gzip."""
    json_string_tasks = json.dumps(tasks_list).replace(" ", "").replace("\n", "")
    compressed_tasks = gzip_str(json_string_tasks)
    # we need to decode back, but only when using Python 3.6
    # when using Python 3.7 it just works
    # Unfortunately the docker image uses Python 3.6
    encoded_tasks = base64.b64encode(compressed_tasks).decode("ascii")

    return encoded_tasks
