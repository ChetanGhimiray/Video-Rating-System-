import os


ALLOWED_EXTENSIONS = {
    "mp4",
    "avi",
    "mov",
    "mkv"
}


def allowed_file(filename):
    """
    Check whether uploaded file has an allowed extension.
    """

    if not filename:
        return False

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def get_safe_filename(filename):
    """
    Create a simple safe filename.
    """

    filename = os.path.basename(filename)

    return filename.replace(" ", "_")
