def generate_feedback(
    fluency,
    eye_contact,
    structure,
    overall
):

    feedback = []

    if fluency >= 80:
        feedback.append(
            "Good speaking fluency."
        )
    else:
        feedback.append(
            "Work on speaking fluency and reduce long pauses."
        )

    if eye_contact >= 80:
        feedback.append(
            "Good audience engagement."
        )
    else:
        feedback.append(
            "Try to maintain more eye contact with the audience."
        )

    if structure >= 80:
        feedback.append(
            "Presentation structure is good."
        )
    else:
        feedback.append(
            "Improve the organization of your presentation."
        )

    if overall >= 80:
        feedback.append(
            "Overall performance is strong."
        )
    else:
        feedback.append(
            "Continue practicing to improve overall performance."
        )

    return feedback