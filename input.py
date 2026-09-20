import os
from urllib.parse import urlparse


ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm"
}


def allowed_file(filename):
    """Check whether a video file has a supported extension."""

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def get_safe_filename(filename):
    """Create a safe filename."""

    filename = os.path.basename(filename)

    return filename.replace(" ", "_")


def is_url(value):
    """Check whether the input looks like a URL."""

    try:
        parsed = urlparse(value)

        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    except Exception:
        return False
