"""
fluency_analysis.py
Member 1: Speech & Audio Analysis

Responsibilities:
- Load faster-whisper locally to transcribe the .wav file
- Extract word timestamps to calculate Words Per Minute (WPM)
- Identify pauses (silent gaps > 1.2 seconds between words)
- Detect filler words (um, uh, like, you know, basically)
"""

import re
from faster_whisper import WhisperModel


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

    Args:
        wav_path (str): Path to the .wav file produced by video_reader.py

    Returns:
        dict: {
            "wpm": float,
            "filler_count": int,
            "pause_count": int,
            "transcript": str
        }
    """

    # 1) Load faster-whisper model locally
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    # 2) Transcribe with word-level timestamps
    segments, info = model.transcribe(
        wav_path,
        word_timestamps=True,
        language="en",
        vad_filter=True,          # skip silence for cleaner segments
    )

    # Materialize generator (faster-whisper returns a generator)
    segments = list(segments)

    # 3) Collect words + build transcript
    words = []          # list of {"word": str, "start": float, "end": float}
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

    # 4) Words Per Minute (WPM)
    if words:
        total_time_sec = words[-1]["end"] - words[0]["start"]
        total_time_min = total_time_sec / 60.0
        wpm = round(len(words) / total_time_min, 2) if total_time_min > 0 else 0.0
    else:
        wpm = 0.0

    # 5) Pause detection (silent gaps > 1.2 s between consecutive words)
    pause_count = 0
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i - 1]["end"]
        if gap > PAUSE_THRESHOLD_SEC:
            pause_count += 1

    # 6) Filler word detection (case-insensitive, whole-word match)
    filler_count = 0
    lower_transcript = transcript.lower()
    for filler in FILLER_WORDS:
        # \b ensures whole-word match; "you know" handled via literal phrase
        pattern = r"\b" + re.escape(filler) + r"\b"
        filler_count += len(re.findall(pattern, lower_transcript))

    # 7) Return in the exact format expected by the pipeline
    return {
        "wpm": wpm,
        "filler_count": filler_count,
        "pause_count": pause_count,
        "transcript": transcript,
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