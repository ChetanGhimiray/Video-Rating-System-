def analyze_fluency(duration):

    score = 80

    # Very short presentation
    if duration < 30:
        score -= 20

    # Very long presentation
    elif duration > 600:
        score -= 10

    return max(0, min(score, 100))