import cv2
import mediapipe as mp


class SpeakerRecognizer:
    """
    Detects whether a visible face/speaker is present in a video.

    This does NOT identify the person's name.
    It detects the presence of a visible speaker.
    """

    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection

    def analyze(self, video_path):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        total_frames = 0
        frames_with_speaker = 0
        max_faces = 0

        with self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        ) as face_detector:

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                total_frames += 1

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detector.process(rgb)

                face_count = 0

                if results.detections:
                    face_count = len(results.detections)

                max_faces = max(max_faces, face_count)

                if face_count > 0:
                    frames_with_speaker += 1

        cap.release()

        if total_frames == 0:
            return {
                "speaker_detected": False,
                "frames_analyzed": 0,
                "face_detected_ratio": 0,
                "maximum_faces_detected": 0
            }

        presence_percentage = (
            frames_with_speaker / total_frames
        ) * 100

        speaker_detected = presence_percentage >= 10

        return {
            "speaker_detected": speaker_detected,
            "frames_analyzed": total_frames,
            "face_detected_ratio": round(
                presence_percentage, 2
            ),
            "maximum_faces_detected": max_faces
        }


def recognize_speaker(video_path):
    recognizer = SpeakerRecognizer()
    return recognizer.analyze(video_path)


if __name__ == "__main__":
    video = input("Enter video path: ")

    try:
        result = recognize_speaker(video)

        print("\n--- SPEAKER RECOGNITION ---")
        print(f"Speaker detected: {result['speaker_detected']}")
        print(
            f"Face detected ratio: "
            f"{result['face_detected_ratio']}%"
        )
        print(
            f"Maximum faces detected: "
            f"{result['maximum_faces_detected']}"
        )

    except Exception as e:
        print(f"Error: {e}")

