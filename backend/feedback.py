def generate_feedback(metrics, scores):
    """Create feedback tied to the actual presentation criteria used in scoring."""
    visual = (metrics or {}).get("visual_metrics", {}) or {}
    fluency = (metrics or {}).get("fluency_metrics", {}) or {}
    delivery = (metrics or {}).get("audio_delivery_metrics", {}) or {}
    transcript = str(fluency.get("transcript", "") or "")
    wpm = float(fluency.get("wpm", 0) or 0)
    filler_count = float(fluency.get("filler_count", 0) or 0)
    eye_contact = float(visual.get("eye_contact_percentage", 0) or 0)
    face_presence = float(visual.get("face_detected_ratio", 0) or 0)
    pitch_range = float(delivery.get("pitch_range_semitones", 0) or 0)
    intensity_range = float(delivery.get("intensity_range_db", 0) or 0)
    pause_ratio = float(delivery.get("pause_ratio", 0) or 0)

    score_breakdown = scores or {}
    content_score = float(score_breakdown.get("content_style", 0) or 0)
    vocal_score = float(score_breakdown.get("vocal_delivery", 0) or 0)
    pace_score = float(score_breakdown.get("pace", 0) or 0)
    fluency_score = float(score_breakdown.get("fluency", 0) or 0)
    eye_score = float(score_breakdown.get("eye_contact", 0) or 0)
    face_score = float(score_breakdown.get("face_presence", 0) or 0)

    feedback = []

    if eye_contact >= 75 and eye_score >= 12:
        feedback.append("Eye contact is strong and helps build trust with the audience. Keep your gaze anchored on the camera when you make key points.")
    elif eye_contact >= 50:
        feedback.append(f"Your eye contact was moderate at {eye_contact:.0f}%. Try looking directly into the camera for your main arguments to feel more confident and engaging.")
    else:
        feedback.append(f"Eye contact was low at {eye_contact:.0f}%, which can make your message feel less personal. Aim to keep your gaze on the camera more consistently.")

    if 130 <= wpm <= 150 and pace_score >= 10:
        feedback.append("Your pacing is balanced and easy to follow. The delivery feels natural, which helps the audience stay engaged.")
    elif wpm > 150:
        feedback.append(f"Your pace is a little fast at {wpm:.0f} WPM, which can make the message feel rushed. Slow down slightly and emphasize key ideas.")
    else:
        feedback.append(f"Your pace is slower than ideal at {wpm:.0f} WPM, which can reduce energy. Try tightening transitions and speaking with a bit more forward momentum.")

    if filler_count <= 3 and fluency_score >= 6:
        feedback.append("Fluency is strong. You are keeping filler words low, which makes your speech sound more polished and confident.")
    elif filler_count <= 8:
        feedback.append(f"You used {filler_count:.0f} filler interruptions, which is manageable but still noticeable. Pausing instead of saying 'um' or 'like' will make the message clearer.")
    else:
        feedback.append(f"Filler words are interrupting your flow. Reducing them will improve clarity and show more control over the message.")

    if content_score >= 12:
        feedback.append("Your content structure is clear and your ideas are connected logically. Keep using signposts like 'first,' 'next,' and 'in conclusion' to guide the audience.")
    else:
        cue_words = ["first", "next", "because", "for example", "therefore", "in conclusion"]
        present = [word for word in cue_words if word.lower() in transcript.lower()]
        if present:
            feedback.append("Your structure is improving, but adding clearer transitions will make the speech easier to follow. Use more signposting between your ideas.")
        else:
            feedback.append("The message would feel stronger with clearer organization. Add transitions such as 'first,' 'next,' and 'in conclusion' to improve flow.")

    if vocal_score >= 8:
        feedback.append("Vocal delivery is well balanced. Your pitch, emphasis, and pause pattern help keep attention on the message.")
    else:
        if pitch_range < 4:
            feedback.append("Your vocal range is fairly narrow. Adding more variation in pitch can make key points sound more deliberate and expressive.")
        elif pause_ratio > 0.18:
            feedback.append("Your pauses are a bit heavy, which can make the rhythm feel uneven. Try smoothing the flow between sentences for a stronger delivery.")
        else:
            feedback.append("Your vocal delivery needs more variety in emphasis and pacing. A little more pitch and energy can make your points land more clearly.")

    if face_presence >= 70:
        feedback.append("Your face presence is visible and consistent, which supports confidence and credibility on camera.")
    elif face_presence >= 40:
        feedback.append("Your face presence is acceptable, but you can improve the framing to keep attention on your delivery and expressions.")
    else:
        feedback.append("The camera framing and face presence were limited. Staying more centered in frame will make your presentation feel more professional.")

    return feedback