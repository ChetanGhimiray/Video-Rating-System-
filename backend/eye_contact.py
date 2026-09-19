import cv2


def analyze_eye_contact(video_path):

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    video = cv2.VideoCapture(video_path)

    total_frames = 0
    frames_with_face = 0

    while True:

        success, frame = video.read()

        if not success:
            break

        total_frames += 1

        # Analyze every 10th frame
        if total_frames % 10 != 0:
            continue

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        if len(faces) > 0:
            frames_with_face += 1

    video.release()

    if total_frames == 0:
        return 0

    score = (
        frames_with_face /
        max(1, total_frames // 10)
    ) * 100

    return round(min(score, 100), 2)