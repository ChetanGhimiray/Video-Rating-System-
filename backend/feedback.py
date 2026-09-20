def generate_feedback(metrics, scores):
    """
    Generates structured strengths and weaknesses based on metric bounds.
    """
    feedback = {"strengths": [], "weaknesses": []}
    
    # Eye contact check
    if metrics["visual_metrics"]["eye_contact_percentage"] >= 75:
        feedback["strengths"].append("Maintained excellent eye contact with the camera throughout the speech.")
    else:
        feedback["weaknesses"].append("Eye contact was low; spent significant time looking away or reading off notes.")

    # WPM check
    wpm = metrics["fluency_metrics"]["wpm"]
    if 130 <= wpm <= 150:
        feedback["strengths"].append("Speech tempo was well-balanced and natural.")
    elif wpm > 150:
        feedback["weaknesses"].append(f"Pacing was slightly fast ({int(wpm)} WPM). Some words may sound rushed.")
    else:
        feedback["weaknesses"].append(f"Pacing was slow ({int(wpm)} WPM), which can reduce audience engagement.")

    return feedback