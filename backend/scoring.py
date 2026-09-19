def calculate_overall(
    speaker_score,
    fluency_score,
    eye_contact_score,
    structure_score
):

    overall = (

        speaker_score * 0.20 +

        fluency_score * 0.30 +

        eye_contact_score * 0.30 +

        structure_score * 0.20

    )

    return round(overall, 2)