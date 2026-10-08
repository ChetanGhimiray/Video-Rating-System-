import math
import wave

import numpy as np


FRAME_SECONDS = 0.03
SILENCE_THRESHOLD_DBFS = -42.0
MIN_PAUSE_SECONDS = 0.3


def _pitch_hz(frame, sample_rate):
    frame = frame.astype(np.float64)
    frame -= np.mean(frame)
    if np.max(np.abs(frame)) < 1:
        return None

    correlation = np.correlate(frame, frame, mode="full")[len(frame) - 1:]
    if correlation[0] <= 0:
        return None
    correlation /= correlation[0]

    min_lag = max(1, int(sample_rate / 400))
    max_lag = min(len(correlation) - 1, int(sample_rate / 70))
    if max_lag <= min_lag:
        return None

    lag = min_lag + int(np.argmax(correlation[min_lag:max_lag + 1]))
    if correlation[lag] < 0.3:
        return None
    return sample_rate / lag


def analyze_audio_delivery(wav_path):
    """Measure approximate pitch, relative intensity, and internal pauses."""
    empty_metrics = {
        "pitch_range_semitones": 0.0,
        "intensity_range_db": 0.0,
        "pause_ratio": 0.0,
        "long_pause_count": 0,
    }

    try:
        with wave.open(wav_path, "rb") as audio_file:
            sample_rate = audio_file.getframerate()
            channels = audio_file.getnchannels()
            sample_width = audio_file.getsampwidth()
            if sample_width != 2 or sample_rate <= 0:
                return empty_metrics
            samples = np.frombuffer(audio_file.readframes(audio_file.getnframes()), dtype="<i2")
    except (OSError, wave.Error, ValueError):
        return empty_metrics

    if channels > 1:
        samples = samples[:len(samples) - len(samples) % channels]
        if not len(samples):
            return empty_metrics
        samples = samples.reshape(-1, channels).mean(axis=1)

    frame_size = max(1, int(sample_rate * FRAME_SECONDS))
    frame_count = len(samples) // frame_size
    if frame_count < 2:
        return empty_metrics

    frames = samples[:frame_count * frame_size].reshape(frame_count, frame_size).astype(np.float64)
    rms = np.sqrt(np.mean(np.square(frames), axis=1))
    dbfs = 20 * np.log10(np.maximum(rms / 32768.0, 1e-8))
    speech_frames = dbfs > SILENCE_THRESHOLD_DBFS
    if not np.any(speech_frames):
        return empty_metrics

    pitch_values = []
    for frame, is_speech in zip(frames, speech_frames):
        if is_speech:
            pitch = _pitch_hz(frame, sample_rate)
            if pitch is not None:
                pitch_values.append(pitch)

    pitch_range = 0.0
    if len(pitch_values) >= 3:
        low, high = np.percentile(pitch_values, [10, 90])
        if low > 0:
            pitch_range = 12 * math.log2(high / low)

    speech_dbfs = dbfs[speech_frames]
    intensity_range = float(np.percentile(speech_dbfs, 90) - np.percentile(speech_dbfs, 10))

    pause_frames = 0
    long_pause_count = 0
    in_pause = False
    pause_length = 0
    for is_speech in speech_frames:
        if not is_speech:
            in_pause = True
            pause_length += 1
        elif in_pause:
            if pause_length * FRAME_SECONDS >= MIN_PAUSE_SECONDS:
                pause_frames += pause_length
                long_pause_count += 1
            in_pause = False
            pause_length = 0

    speech_duration = int(np.count_nonzero(speech_frames)) * FRAME_SECONDS
    pause_duration = pause_frames * FRAME_SECONDS
    pause_ratio = pause_duration / (speech_duration + pause_duration) if speech_duration else 0.0

    return {
        "pitch_range_semitones": round(float(pitch_range), 2),
        "intensity_range_db": round(intensity_range, 2),
        "pause_ratio": round(pause_ratio, 3),
        "long_pause_count": long_pause_count,
    }