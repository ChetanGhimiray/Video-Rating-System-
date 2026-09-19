import cv2


def read_video(video_path):

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise Exception("Unable to open video")

    fps = video.get(cv2.CAP_PROP_FPS)

    frame_count = video.get(
        cv2.CAP_PROP_FRAME_COUNT
    )

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    if fps > 0:
        duration = frame_count / fps
    else:
        duration = 0

    video.release()

    return {
        "fps": fps,
        "frames": frame_count,
        "duration": duration,
        "width": width,
        "height": height
    }