import os
import subprocess
import requests
from urllib.parse import urlparse


ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm"
}


def get_extension_from_url(url):
    """Get video extension from URL."""

    path = urlparse(url).path

    extension = os.path.splitext(path)[1].lower()

    if extension in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        return extension

    return ".mp4"


def download_video(url, output_dir="uploads"):
    """
    Download a video from a direct video URL.
    """

    os.makedirs(output_dir, exist_ok=True)

    extension = get_extension_from_url(url)

    video_path = os.path.join(
        output_dir,
        "downloaded_video" + extension
    )

    response = requests.get(
        url,
        stream=True,
        timeout=60
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    if not (
        "video" in content_type
        or extension in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    ):
        raise ValueError(
            "The URL does not appear to be a direct video URL."
        )

    with open(video_path, "wb") as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                file.write(chunk)

    return video_path


def extract_audio(video_path, output_dir="processed"):
    """
    Extract WAV audio from video using FFmpeg.
    """

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.splitext(
        os.path.basename(video_path)
    )[0]

    audio_path = os.path.join(
        output_dir,
        filename + ".wav"
    )

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
        "-y"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg audio extraction failed:\n"
            + result.stderr
        )

    return audio_path
