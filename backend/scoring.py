import re


SPEAKING_STYLES = {
    "motivational": {
        "label": "Motivational",
        "cues": ["believe", "achieve", "together", "overcome", "success", "you can", "you will", "keep going", "your goal", "your future"],
        "pitch_target": 6.0,
        "intensity_target": 9.0,
        "pause_target": 0.12,
    },
    "lecture": {
        "label": "Lecture",
        "cues": ["first", "second", "next", "for example", "therefore", "because", "in conclusion", "to summarize", "in other words", "according to"],
        "pitch_target": 4.5,
        "intensity_target": 7.0,
        "pause_target": 0.10,
    },
    "conversational": {
        "label": "Conversational / plain speaking",
        "cues": ["I think", "I mean", "you know", "well", "actually", "kind of", "sort of", "by the way", "I guess", "to be honest"],
        "pitch_target": 4.0,
        "intensity_target": 6.0,
        "pause_target": 0.10,
    },
}

ORGANIZATION_CUES = ["because", "for example", "but", "so", "first", "then", "finally", "in conclusion", "however", "therefore"]


def _safe_number(value, default=0.0):
    if value is None:
        return default

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if number != number or abs(number) == float("inf"):
        return default

    return number


def _count_phrases(text, phrases):
    count = 0
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\b"
        count += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return count


def calculate_scores(metrics):
    """
    Combines raw metrics into category grades and a total score out of 100.
    Uses a realistic presentation rubric and safe defaults for incomplete data.
    """
    if not isinstance(metrics, dict):
        return {
            "total_score": 0.0,
            "breakdown": {
                "content_style": 0.0,
                "vocal_delivery": 0.0,
                "pace": 0.0,
                "fluency": 0.0,
                "eye_contact": 0.0,
                "face_presence": 0.0,
            }
        }

    fluency = metrics.get("fluency_metrics", {}) or {}
    visual = metrics.get("visual_metrics", {}) or {}
    delivery = metrics.get("audio_delivery_metrics", {}) or {}
    transcript = str(fluency.get("transcript", "") or "")
    speaking_style = metrics.get("speaking_style", "conversational")
    if speaking_style not in SPEAKING_STYLES:
        speaking_style = "conversational"
    style = SPEAKING_STYLES[speaking_style]

    eye_contact = max(0.0, min(100.0, _safe_number(visual.get("eye_contact_percentage", 0), 0.0)))
    face_presence = max(0.0, min(100.0, _safe_number(visual.get("face_detected_ratio", 0), 0.0)))
    wpm = max(0.0, _safe_number(fluency.get("wpm", 0), 0.0))
    filler_count = max(0.0, _safe_number(fluency.get("filler_count", 0), 0.0))
    pitch_range = max(0.0, _safe_number(delivery.get("pitch_range_semitones", 0), 0.0))
    intensity_range = max(0.0, _safe_number(delivery.get("intensity_range_db", 0), 0.0))
    pause_ratio = max(0.0, min(1.0, _safe_number(delivery.get("pause_ratio", 0), 0.0)))

    words = re.findall(r"\b[\w']+\b", transcript)
    cue_count = _count_phrases(transcript, style["cues"])
    organization_count = _count_phrases(transcript, ORGANIZATION_CUES)
    if len(words) >= 8:
        content_score = min(20.0, cue_count * 50.0 / len(words))
        organization_score = min(10.0, organization_count * 2.0)
    else:
        content_score = 0.0
        organization_score = 0.0
    content_style_score = content_score + organization_score

    # Acoustic targets are heuristics and are intentionally style-dependent.
    pitch_score = 10.0 * max(0.0, 1.0 - abs(pitch_range - style["pitch_target"]) / 10.0)
    intensity_score = 7.0 * max(0.0, 1.0 - abs(intensity_range - style["intensity_target"]) / 12.0)
    pause_score = 8.0 * max(0.0, 1.0 - abs(pause_ratio - style["pause_target"]) / 0.20)
    vocal_delivery_score = pitch_score + intensity_score + pause_score

    # A steady pace earns up to 15 points.
    if 130 <= wpm <= 150:
        pace_score = 15.0
    elif wpm <= 0:
        pace_score = 0.0
    elif wpm < 130:
        pace_score = max(0.0, 15.0 - ((130 - wpm) * 0.125))
    else:
        pace_score = max(0.0, 15.0 - ((wpm - 150) * 0.11))

    filler_score = max(0.0, 10.0 - (filler_count * 0.9))

    eye_score = eye_contact * 0.18
    face_score = face_presence * 0.02

    breakdown = {
        "content_style": round(content_style_score, 1),
        "vocal_delivery": round(vocal_delivery_score, 1),
        "pace": round(pace_score, 1),
        "fluency": round(filler_score, 1),
        "eye_contact": round(eye_score, 1),
        "face_presence": round(face_score, 1),
    }
    total_score = round(sum(breakdown.values()), 2)

    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "speaking_style": speaking_style,
        "content_style_metrics": {
            "context_cues": cue_count,
            "organization_cues": organization_count,
        },
    }