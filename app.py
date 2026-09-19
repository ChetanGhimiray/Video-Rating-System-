from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

import os

from database.db import (
    create_database,
    add_student,
    get_student,
    get_next_presentation_number,
    add_presentation,
    get_presentations,
    get_presentation
)

from backend.video_reader import read_video

from backend.duplicate_detector import (
    get_file_hash
)

from backend.speaker_recognition import (
    recognize_speaker
)

from backend.fluency_analysis import (
    analyze_fluency
)

from backend.eye_contact import (
    analyze_eye_contact
)

from backend.scoring import (
    calculate_overall
)

from backend.feedback import (
    generate_feedback
)

from backend.improvement import (
    calculate_improvement,
    calculate_average
)


app = Flask(__name__)


UPLOAD_FOLDER = "uploads/videos"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


create_database()


# ------------------------------------------------
# HOME
# ------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")


# ------------------------------------------------
# STUDENT PAGE
# ------------------------------------------------

@app.route("/student", methods=["GET", "POST"])
def student():

    if request.method == "POST":

        student_id = request.form["student_id"]

        name = request.form["name"]

        add_student(
            student_id,
            name
        )

        return redirect(
            url_for(
                "student_profile",
                student_id=student_id
            )
        )

    return render_template(
        "student.html"
    )


# ------------------------------------------------
# STUDENT PROFILE
# ------------------------------------------------

@app.route("/student/<student_id>")
def student_profile(student_id):

    student_data = get_student(student_id)

    if not student_data:

        return "Student not found"

    presentations = get_presentations(
        student_id
    )

    average = calculate_average(
        presentations
    )

    improvement = calculate_improvement(
        presentations
    )

    return render_template(
        "progress.html",
        student=student_data,
        presentations=presentations,
        average=average,
        improvement=improvement
    )


# ------------------------------------------------
# UPLOAD PAGE
# ------------------------------------------------

@app.route("/upload/<student_id>")
def upload(student_id):

    student_data = get_student(student_id)

    if not student_data:

        return "Student not found"

    next_number = get_next_presentation_number(
        student_id
    )

    return render_template(
        "upload.html",
        student=student_data,
        presentation_number=next_number
    )


# ------------------------------------------------
# PROCESS VIDEO
# ------------------------------------------------

@app.route(
    "/process/<student_id>",
    methods=["POST"]
)
def process_video(student_id):

    student_data = get_student(student_id)

    if not student_data:

        return "Student not found"

    video = request.files.get("video")

    if not video:

        return "No video selected"

    if video.filename == "":

        return "Invalid video"

    presentation_number = (
        get_next_presentation_number(
            student_id
        )
    )

    filename = video.filename

    video_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    video.save(video_path)

    # --------------------------------------------
    # Read video
    # --------------------------------------------

    video_information = read_video(
        video_path
    )

    duration = video_information[
        "duration"
    ]

    # --------------------------------------------
    # Duplicate detection
    # --------------------------------------------

    video_hash = get_file_hash(
        video_path
    )

    # --------------------------------------------
    # Speaker
    # --------------------------------------------

    speaker_result = recognize_speaker(
        student_id
    )

    speaker_score = speaker_result[
        "speaker_score"
    ]

    # --------------------------------------------
    # Fluency
    # --------------------------------------------

    fluency_score = analyze_fluency(
        duration
    )

    # --------------------------------------------
    # Eye contact
    # --------------------------------------------

    eye_contact_score = analyze_eye_contact(
        video_path
    )

    # --------------------------------------------
    # Structure
    # --------------------------------------------

    structure_score = 80

    # --------------------------------------------
    # Overall score
    # --------------------------------------------

    overall_score = calculate_overall(

        speaker_score,

        fluency_score,

        eye_contact_score,

        structure_score
    )

    # --------------------------------------------
    # Feedback
    # --------------------------------------------

    feedback_list = generate_feedback(

        fluency_score,

        eye_contact_score,

        structure_score,

        overall_score
    )

    feedback = "\n".join(
        feedback_list
    )

    # --------------------------------------------
    # Save to database
    # --------------------------------------------

    presentation_data = {

        "student_id":
            student_id,

        "presentation_number":
            presentation_number,

        "video_name":
            filename,

        "video_hash":
            video_hash,

        "duration":
            duration,

        "speaker_score":
            speaker_score,

        "fluency_score":
            fluency_score,

        "eye_contact_score":
            eye_contact_score,

        "structure_score":
            structure_score,

        "overall_score":
            overall_score,

        "feedback":
            feedback
    }

    presentation_id = add_presentation(
        presentation_data
    )

    return redirect(
        url_for(
            "result",
            presentation_id=presentation_id
        )
    )


# ------------------------------------------------
# RESULT
# ------------------------------------------------

@app.route("/result/<int:presentation_id>")
def result(presentation_id):

    presentation = get_presentation(
        presentation_id
    )

    if not presentation:

        return "Presentation not found"

    return render_template(
        "result.html",
        presentation=presentation
    )


# ------------------------------------------------
# OVERALL PERFORMANCE
# ------------------------------------------------

@app.route("/overall/<student_id>")
def overall(student_id):

    student_data = get_student(
        student_id
    )

    if not student_data:

        return "Student not found"

    presentations = get_presentations(
        student_id
    )

    average = calculate_average(
        presentations
    )

    improvement = calculate_improvement(
        presentations
    )

    return render_template(
        "overall.html",
        student=student_data,
        presentations=presentations,
        average=average,
        improvement=improvement
    )


# ------------------------------------------------
# RUN
# ------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )