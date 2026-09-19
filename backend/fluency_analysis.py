import re
from faster_whisper import WhisperModel


class FluencyAnalyzer:
    """
    Analyzes speaking fluency using Faster-Whisper.
    """

    def __init__(
        self,
        model_size="base",
        device="cpu",
        compute_type="int8"
    ):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        self.filler_words = {
            "um",
            "uh",
            "erm",
            "hmm",
            "like",
            "actually",
            "basically",
            "you know",
            "i mean"
        }

    def transcribe(self, video_path):

        segments, info = self.model.transcribe(
            video_path,
            beam_size=5,
            vad_filter=True
        )

        segment_list = []

        for segment in segments:
            segment_list.append({
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text.strip()
            })

        return segment_list

    def count_words(self, text):

        words = re.findall(
            r"\b[\w']+\b",
            text.lower()
        )

        return words

    def count_filler_words(self, words):

        filler_count = 0

        for word in words:

            if word.lower() in self.filler_words:
                filler_count += 1

        return filler_count

    def calculate_long_pauses(
        self,
        segments,
        pause_threshold=2.0
    ):

        long_pauses = 0
        total_pause_time = 0.0

        for i in range(1, len(segments)):

            previous_end = segments[i - 1]["end"]
            current_start = segments[i]["start"]

            pause = current_start - previous_end

            if pause >= pause_threshold:
                long_pauses += 1
                total_pause_time += pause

        return long_pauses, total_pause_time

    def calculate_fluency_score(
        self,
        wpm,
        filler_words,
        long_pauses,
        speaking_time
    ):

        score = 100.0

        # WPM component
        # Normal presentation range is approximately
        # 100-160 words per minute.
        if wpm < 60:
            score -= 25

        elif wpm < 80:
            score -= 15

        elif wpm < 100:
            score -= 5

        elif wpm > 180:
            score -= 20

        elif wpm > 160:
            score -= 10

        # Filler word penalty
        if speaking_time > 0:

            filler_rate = (
                filler_words / speaking_time
            ) * 60

            score -= min(
                filler_rate * 2,
                20
            )

        # Long pause penalty
        score -= min(
            long_pauses * 3,
            20
        )

        score = max(
            0,
            min(100, score)
        )

        return round(score, 2)

    def analyze(self, video_path):

        segments = self.transcribe(video_path)

        if not segments:
            return {
                "fluency_score": 0,
                "transcript": "",
                "words_spoken": 0,
                "words_per_minute": 0,
                "filler_words": 0,
                "long_pauses": 0,
                "speaking_time_seconds": 0,
                "pause_time_seconds": 0
            }

        transcript = " ".join(
            segment["text"]
            for segment in segments
        )

        words = self.count_words(transcript)

        words_spoken = len(words)

        speaking_time = sum(
            segment["end"] - segment["start"]
            for segment in segments
        )

        long_pauses, pause_time = (
            self.calculate_long_pauses(segments)
        )

        filler_words = self.count_filler_words(words)

        if speaking_time > 0:
            wpm = (
                words_spoken / speaking_time
            ) * 60
        else:
            wpm = 0

        score = self.calculate_fluency_score(
            wpm,
            filler_words,
            long_pauses,
            speaking_time
        )

        return {
            "fluency_score": score,
            "transcript": transcript,
            "words_spoken": words_spoken,
            "words_per_minute": round(wpm, 2),
            "filler_words": filler_words,
            "long_pauses": long_pauses,
            "speaking_time_seconds": round(
                speaking_time,
                2
            ),
            "pause_time_seconds": round(
                pause_time,
                2
            )
        }


def analyze_fluency(video_path):

    analyzer = FluencyAnalyzer()

    return analyzer.analyze(video_path)


if __name__ == "__main__":

    video = input("Enter video path: ")

    try:

        result = analyze_fluency(video)

        print("\n--- FLUENCY ANALYSIS ---")

        print(
            f"Fluency score: "
            f"{result['fluency_score']}/100"
        )

        print(
            f"Words spoken: "
            f"{result['words_spoken']}"
        )

        print(
            f"Words per minute: "
            f"{result['words_per_minute']}"
        )

        print(
            f"Filler words: "
            f"{result['filler_words']}"
        )

        print(
            f"Long pauses: "
            f"{result['long_pauses']}"
        )

        print(
            f"Speaking time: "
            f"{result['speaking_time_seconds']} seconds"
        )

        print("\nTranscript:")
        print(result["transcript"])

    except Exception as e:
        print(f"Error: {e}")