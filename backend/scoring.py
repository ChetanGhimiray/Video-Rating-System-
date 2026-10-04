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


def calculate_scores(metrics):
    """
    Combines raw metrics into category grades and a total score out of 100.
    Uses a realistic presentation rubric and safe defaults for incomplete data.
    """
    if not isinstance(metrics, dict):
        return {
            "total_score": 0.0,
            "breakdown": {
                "eye_contact": 0.0,
                "pace": 0.0,
                "clarity": 0.0,
                "flow": 0.0
            }
        }

    fluency = metrics.get("fluency_metrics", {}) or {}
    visual = metrics.get("visual_metrics", {}) or {}

    eye_contact = max(0.0, min(100.0, _safe_number(visual.get("eye_contact_percentage", 0), 0.0)))
    wpm = max(0.0, _safe_number(fluency.get("wpm", 0), 0.0))
    filler_count = max(0.0, _safe_number(fluency.get("filler_count", 0), 0.0))
    pause_count = max(0.0, _safe_number(fluency.get("pause_count", 0), 0.0))

    # Eye contact deserves a strong weight in presentation quality.
    eye_score = min(25.0, (eye_contact / 100.0) * 25.0)

    # Ideal pace is steady and natural, around 130-150 WPM.
    if 130 <= wpm <= 150:
        pace_score = 30.0
    elif wpm <= 0:
        pace_score = 10.0
    elif wpm < 130:
        pace_score = max(0.0, 30.0 - ((130 - wpm) * 0.25))
    else:
        pace_score = max(0.0, 30.0 - ((wpm - 150) * 0.22))

    # Clarity penalizes filler words without being overly harsh.
    filler_score = max(0.0, 20.0 - (filler_count * 1.8))

    # Flow rewards natural pauses and penalizes broken speech.
    pause_score = max(0.0, 15.0 - (pause_count * 1.5))

    total_score = round(max(0.0, min(100.0, eye_score + pace_score + filler_score + pause_score)), 2)

    return {
        "total_score": total_score,
        "breakdown": {
            "eye_contact": round(eye_score, 1),
            "pace": round(pace_score, 1),
            "clarity": round(filler_score, 1),
            "flow": round(pause_score, 1)
        }
    }