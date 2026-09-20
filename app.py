from flask import (
    Flask,
    request,
    render_template
)

import os

from input import (
    allowed_file,
    get_safe_filename,
    is_url
)

from video_reader import (
    download_video,
    extract_audio
)

from database.database import (
    initialize_database,
    save_result
)


app = Flask(__name__)


UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    PROCESSED_FOLDER,
    exist_ok=True
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# UPLOAD / URL
# --------------------------------------------------

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    uploaded_file = request.files.get(
        "video"
    )

    video_url = request.form.get(
        "video_url",
        ""
    ).strip()


    # ----------------------------------------------
    # CHECK INPUT
    # ----------------------------------------------

    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ) and not video_url:

        return render_template(
            "index.html",
            error="Please upload a video or enter a video URL."
        )


    # ----------------------------------------------
    # OPTION 1: UPLOAD FILE
    # ----------------------------------------------

    if (
        uploaded_file
        and uploaded_file.filename
    ):

        filename = get_safe_filename(
            uploaded_file.filename
        )

        if not allowed_file(filename):

            return render_template(
                "index.html",
                error=(
                    "Unsupported video format. "
                    "Use MP4, MOV, AVI, MKV or WebM."
                )
            )


        video_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        uploaded_file.save(
            video_path
        )


        source = "Uploaded File"


    # ----------------------------------------------
    # OPTION 2: VIDEO URL
    # ----------------------------------------------

    elif video_url:

        if not is_url(video_url):

            return render_template(
                "index.html",
                error="Please enter a valid HTTP/HTTPS URL."
            )


        try:

            video_path = download_video(
                video_url,
                UPLOAD_FOLDER
            )

            filename = os.path.basename(
                video_path
            )

            source = video_url


        except Exception as error:

            return render_template(
                "index.html",
                error=f"Video download failed: {error}"
            )


    # ----------------------------------------------
    # EXTRACT AUDIO
    # ----------------------------------------------

    try:

        audio_path = extract_audio(
            video_path,
            PROCESSED_FOLDER
        )

    except Exception as error:

        return render_template(
            "index.html",
            error=f"Audio extraction failed: {error}"
        )


    # =================================================
    # MEMBER 1
    # =================================================

    # TEMPORARY DATA
    #
    # We will replace this with:
    #
    # from fluency_analysis import analyze_audio
    #
    # fluency_data = analyze_audio(audio_path)

    fluency_data = {

        "wpm": 0,

        "filler_count": 0,

        "pause_count": 0,

        "transcript": ""

    }


    # =================================================
    # MEMBER 2
    # =================================================

    # TEMPORARY DATA
    #
    # We will replace this with the actual
    # eye_contact.py and speaker_recognition.py

    visual_data = {

        "eye_contact_percentage": 0,

        "face_detected_ratio": 0

    }


    # =================================================
    # COMBINE MEMBER 1 + MEMBER 2
    # =================================================

    processed_data = {

        "visual_metrics": visual_data,

        "fluency_metrics": fluency_data

    }


    # =================================================
    # MEMBER 3
    # =================================================

    # TEMPORARY SCORE
    #
    # Later:
    #
    # score = calculate_score(processed_data)

    final_score = 0


    feedback = []


    # =================================================
    # DATABASE
    # =================================================

    database_data = {

        "video_filename": filename,

        "video_source": source,

        "wpm":
            fluency_data["wpm"],

        "filler_count":
            fluency_data["filler_count"],

        "pause_count":
            fluency_data["pause_count"],

        "eye_contact_percentage":
            visual_data[
                "eye_contact_percentage"
            ],

        "face_detected_ratio":
            visual_data[
                "face_detected_ratio"
            ],

        "final_score":
            final_score,

        "transcript":
            fluency_data["transcript"],

        "feedback":
            "\n".join(feedback)

    }


    submission_id = save_result(
        database_data
    )


    # =================================================
    # RESULT
    # =================================================

    return render_template(

        "result.html",

        data=processed_data,

        score=final_score,

        feedback=feedback,

        submission_id=submission_id,

        video_filename=filename,

        video_source=source,

        audio_path=audio_path

    )


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
