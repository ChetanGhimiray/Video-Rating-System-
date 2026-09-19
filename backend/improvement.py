def generate_actionable_tips(metrics):
    """
    Generates concrete practice goals based on areas needing work.
    """
    tips = []
    fluency = metrics["fluency_metrics"]
    visual = metrics["visual_metrics"]

    if visual["eye_contact_percentage"] < 70:
        tips.append("Position your camera directly at eye level and place sticky notes next to the lens instead of looking down at a desk.")

    if fluency["filler_count"] > 5:
        tips.append(f"You used {fluency['filler_count']} filler words. Try replacing words like 'um' or 'uh' with deliberate 1-second pauses.")

    if fluency["wpm"] > 160:
        tips.append("Practice using a metronome or timing yourself to slow down speech pace closer to 140 WPM.")

    if not tips:
        tips.append("Great overall delivery! Focus on maintaining natural gesture movement to enhance engagement further.")

    return tips