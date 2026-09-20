def calculate_scores(metrics):
    """
    Combines raw metrics into category grades and a total score out of 100.
    """
    fluency = metrics["fluency_metrics"]
    visual = metrics["visual_metrics"]

    # 1. Eye Contact Score (Max 25 pts)
    eye_score = min(25.0, (visual["eye_contact_percentage"] / 100.0) * 25.0)

    # 2. Speech Pace Score (Max 35 pts) - Ideal WPM is 130 to 150
    wpm = fluency["wpm"]
    if 130 <= wpm <= 150:
        pace_score = 35.0
    elif wpm < 130:
        pace_score = max(0.0, 35.0 - (130 - wpm) * 0.3)
    else:
        pace_score = max(0.0, 35.0 - (wpm - 150) * 0.3)

    # 3. Delivery Clarity & Fillers (Max 20 pts)
    fillers = fluency["filler_count"]
    filler_score = max(0.0, 20.0 - (fillers * 1.5))

    # 4. Pauses & Flow (Max 20 pts)
    pauses = fluency["pause_count"]
    pause_score = max(0.0, 20.0 - (pauses * 2.0))

    # Total Score
    total_score = round(eye_score + pace_score + filler_score + pause_score, 2)

    return {
        "total_score": total_score,
        "breakdown": {
            "eye_contact": round(eye_score, 1),
            "pace": round(pace_score, 1),
            "clarity": round(filler_score, 1),
            "flow": round(pause_score, 1)
        }
    }