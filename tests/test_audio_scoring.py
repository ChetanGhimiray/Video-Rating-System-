import math
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from backend.audio_delivery import analyze_audio_delivery
from backend.feedback import generate_feedback
from backend.scoring import calculate_scores


class AudioDeliveryTests(unittest.TestCase):
    def test_measures_pitch_intensity_and_internal_pause(self):
        sample_rate = 16000
        first_tone = 0.2 * np.sin(2 * math.pi * 110 * np.arange(sample_rate) / sample_rate)
        silence = np.zeros(sample_rate // 2)
        second_tone = 0.5 * np.sin(2 * math.pi * 220 * np.arange(sample_rate) / sample_rate)
        samples = np.concatenate((first_tone, silence, second_tone))
        pcm_samples = np.int16(samples * 32767)

        with tempfile.TemporaryDirectory() as temporary_directory:
            wav_path = Path(temporary_directory) / "delivery.wav"
            with wave.open(str(wav_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_samples.tobytes())

            metrics = analyze_audio_delivery(str(wav_path))

        self.assertGreater(metrics["pitch_range_semitones"], 6)
        self.assertGreater(metrics["intensity_range_db"], 3)
        self.assertAlmostEqual(metrics["pause_ratio"], 0.2, delta=0.04)
        self.assertEqual(metrics["long_pause_count"], 1)


class ScoringTests(unittest.TestCase):
    def test_breakdown_is_out_of_100_and_context_changes_cue_score(self):
        metrics = {
            "speaking_style": "motivational",
            "fluency_metrics": {
                "transcript": "You can believe and achieve your goal. Keep going together. First, we begin because examples help.",
                "wpm": 140,
                "filler_count": 0,
            },
            "audio_delivery_metrics": {
                "pitch_range_semitones": 6,
                "intensity_range_db": 9,
                "pause_ratio": 0.12,
            },
            "visual_metrics": {
                "eye_contact_percentage": 100,
                "face_detected_ratio": 100,
            },
        }

        motivational_result = calculate_scores(metrics)
        metrics["speaking_style"] = "lecture"
        lecture_result = calculate_scores(metrics)

        self.assertLessEqual(motivational_result["total_score"], 100)
        self.assertEqual(sum(motivational_result["breakdown"].values()), motivational_result["total_score"])
        self.assertGreater(
            motivational_result["breakdown"]["content_style"],
            lecture_result["breakdown"]["content_style"],
        )

    def test_feedback_references_criteria(self):
        metrics = {
            "speaking_style": "motivational",
            "fluency_metrics": {
                "transcript": "You can do this. First, focus on your goal. Keep going together.",
                "wpm": 165,
                "filler_count": 8,
            },
            "audio_delivery_metrics": {
                "pitch_range_semitones": 3,
                "intensity_range_db": 5,
                "pause_ratio": 0.2,
            },
            "visual_metrics": {
                "eye_contact_percentage": 42,
                "face_detected_ratio": 60,
            },
        }
        scores = {
            "content_style": 12,
            "vocal_delivery": 6,
            "pace": 8,
            "fluency": 3,
            "eye_contact": 9,
            "face_presence": 1,
        }

        feedback = generate_feedback(metrics, scores)

        self.assertTrue(any("eye contact" in item.lower() for item in feedback))
        self.assertTrue(any("pace" in item.lower() or "tempo" in item.lower() for item in feedback))
        self.assertTrue(any("filler" in item.lower() or "fluency" in item.lower() for item in feedback))


if __name__ == "__main__":
    unittest.main()