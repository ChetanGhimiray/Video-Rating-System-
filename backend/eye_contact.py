import cv2
import mediapipe as mp
import numpy as np


class EyeContactAnalyzer:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.LEFT_EYE = [
            33,
            133,
            160,
            159,
            158,
            157,
            173
        ]

        self.RIGHT_EYE = [
            362,
            263,
            387,
            386,
            385,
            384,
            398
        ]

        self.LEFT_IRIS = [
            468,
            469,
            470,
            471,
            472
        ]

        self.RIGHT_IRIS = [
            473,
            474,
            475,
            476,
            477
        ]

    def landmark_point(
        self,
        landmark,
        width,
        height
    ):

        return np.array([
            landmark.x * width,
            landmark.y * height
        ])

    def eye_ratio(
        self,
        eye_landmarks,
        iris_landmarks,
        face_landmarks,
        width,
        height
    ):

        eye_points = [
            self.landmark_point(
                face_landmarks[i],
                width,
                height
            )
            for i in eye_landmarks
        ]

        iris_points = [
            self.landmark_point(
                face_landmarks[i],
                width,
                height
            )
            for i in iris_landmarks
        ]

        eye_left = eye_points[0]
        eye_right = eye_points[1]

        iris_center = np.mean(
            iris_points,
            axis=0
        )

        eye_width = np.linalg.norm(
            eye_right - eye_left
        )

        if eye_width == 0:
            return 0.5

        horizontal_position = (
            iris_center[0] - eye_left[0]
        ) / eye_width

        return horizontal_position

    def is_looking_at_camera(
        self,
        face_landmarks,
        width,
        height
    ):

        left_ratio = self.eye_ratio(
            self.LEFT_EYE,
            self.LEFT_IRIS,
            face_landmarks,
            width,
            height
        )

        right_ratio = self.eye_ratio(
            self.RIGHT_EYE,
            self.RIGHT_IRIS,
            face_landmarks,
            width,
            height
        )

        average_ratio = (
            left_ratio + right_ratio
        ) / 2

        # Approximate camera-looking range.
        return 0.35 <= average_ratio <= 0.65

    def analyze(
        self,
        video_path,
        sample_every_n_frames=5
    ):

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(
                f"Could not open video: {video_path}"
            )

        total_checked = 0
        face_frames = 0
        eye_contact_frames = 0

        with self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:

            frame_number = 0

            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                frame_number += 1

                if (
                    frame_number
                    % sample_every_n_frames
                    != 0
                ):
                    continue

                total_checked += 1

                height, width = frame.shape[:2]

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                results = face_mesh.process(rgb)

                if not results.multi_face_landmarks:
                    continue

                face_frames += 1

                face_landmarks = (
                    results.multi_face_landmarks[0]
                    .landmark
                )

                looking = self.is_looking_at_camera(
                    face_landmarks,
                    width,
                    height
                )

                if looking:
                    eye_contact_frames += 1

        cap.release()

        if face_frames == 0:

            return {
                "eye_contact_score": 0,
                "eye_contact_percentage": 0,
                "looking_away_percentage": 100,
                "frames_with_face": 0
            }

        eye_contact_percentage = (
            eye_contact_frames / face_frames
        ) * 100

        looking_away_percentage = (
            100 - eye_contact_percentage
        )

        return {
            "eye_contact_score": round(
                eye_contact_percentage,
                2
            ),
            "eye_contact_percentage": round(
                eye_contact_percentage,
                2
            ),
            "looking_away_percentage": round(
                looking_away_percentage,
                2
            ),
            "frames_checked": total_checked,
            "frames_with_face": face_frames
        }


def analyze_eye_contact(video_path):

    analyzer = EyeContactAnalyzer()

    return analyzer.analyze(video_path)


if __name__ == "__main__":

    video = input("Enter video path: ")

    try:

        result = analyze_eye_contact(video)

        print("\n--- EYE CONTACT ANALYSIS ---")

        print(
            f"Eye contact score: "
            f"{result['eye_contact_score']}/100"
        )

        print(
            f"Eye contact: "
            f"{result['eye_contact_percentage']}%"
        )

        print(
            f"Looking away: "
            f"{result['looking_away_percentage']}%"
        )

    except Exception as e:
        print(f"Error: {e}")