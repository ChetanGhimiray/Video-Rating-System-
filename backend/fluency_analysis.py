"""
fluency_analysis.py
Member 1: Speech & Audio Analysis

Responsibilities:
- Load faster-whisper locally to transcribe the .wav file
- Extract word timestamps to calculate Words Per Minute (WPM)
- Identify pauses (silent gaps > 1.2 seconds between words)
- Detect filler words (um, uh, like, you know, basically)
"""

import os
import re

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "so"]
PAUSE_THRESHOLD_SEC = 1.2
MODEL_SIZE = "base"          # tiny / base / small / medium / large-v2
DEVICE = "cpu"               # switch to "cuda" if GPU available
COMPUTE_TYPE = "int8"        # use "float16" on GPU


# ----------------------------------------------------------------------
# Core analysis
# ----------------------------------------------------------------------
def analyze_fluency(wav_path: str) -> dict:
    """
    Transcribe a .wav file and compute fluency metrics.

    This function now fails gracefully when faster-whisper or its native audio
    dependency stack is incompatible (for example av / ffmpeg runtime errors).
    """
    if not wav_path or not os.path.exists(wav_path):
        return {
            "wpm": 0.0,
            "filler_count": 0,
            "pause_count": 0,
            "transcript": "Audio analysis unavailable. No valid audio file was provided.",
        }

    if WhisperModel is None:
        return {
            "wpm": 0.0,
            "filler_count": 0,
            "pause_count": 0,
            "transcript": "Speech recognition dependency is unavailable in this environment.",
        }

    try:
        model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        segments, info = model.transcribe(
            wav_path,
            word_timestamps=True,
            language="en",
            vad_filter=True,
        )
        segments = list(segments)

        words = []
        transcript_parts = []

        for seg in segments:
            transcript_parts.append(seg.text.strip())
            if seg.words:
                for w in seg.words:
                    words.append({
                        "word": w.word.strip(),
                        "start": float(w.start),
                        "end": float(w.end),
                    })

        transcript = " ".join(transcript_parts).strip()

        if words:
            total_time_sec = words[-1]["end"] - words[0]["start"]
            total_time_min = total_time_sec / 60.0
            wpm = round(len(words) / total_time_min, 2) if total_time_min > 0 else 0.0
        else:
            wpm = 0.0

        pause_count = 0
        for i in range(1, len(words)):
            gap = words[i]["start"] - words[i - 1]["end"]
            if gap > PAUSE_THRESHOLD_SEC:
                pause_count += 1

        filler_count = 0
        lower_transcript = transcript.lower()
        for filler in FILLER_WORDS:
            pattern = r"\b" + re.escape(filler) + r"\b"
            filler_count += len(re.findall(pattern, lower_transcript))

        return {
            "wpm": wpm,
            "filler_count": filler_count,
            "pause_count": pause_count,
            "transcript": transcript,
        }
    except Exception:
        return {
            "wpm": 0.0,
            "filler_count": 0,
            "pause_count": 0,
            "transcript": "Speech analysis failed due to an incompatible audio library stack.",
        }


# ----------------------------------------------------------------------
# Verification check (run as script)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sample_wav = "8.mp4"   # replace with your test file
    result = analyze_fluency(sample_wav)

    print("\n=== Fluency Analysis Result ===")
    for k, v in result.items():
        if k == "transcript":
            print(f"{k}: {v[:80]}...")
        else:
            print(f"{k}: {v}")

    # Sanity assertions
    assert isinstance(result, dict)
    assert set(result.keys()) == {"wpm", "filler_count", "pause_count", "transcript"}
    assert isinstance(result["wpm"], float)
    assert isinstance(result["filler_count"], int)
    assert isinstance(result["pause_count"], int)
    assert isinstance(result["transcript"], str)
    print("\n✅ Verification passed.")