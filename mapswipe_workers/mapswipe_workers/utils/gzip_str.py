import gzip
import io


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
