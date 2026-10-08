from functools import wraps
import json
import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from input import allowed_file, get_safe_filename, is_url

from backend.video_reader import download_video, extract_audio
from backend.fluency_analysis import analyze_fluency
from backend.audio_delivery import analyze_audio_delivery
from backend.eye_contact import analyze_eye_contact
from backend.speaker_recognition import recognize_speaker
from backend.scoring import calculate_scores, SPEAKING_STYLES
from backend.feedback import generate_feedback

from database.db import (
    create_user,
    get_recent_results,
    get_submission,
    get_submission_summary,
    get_user_by_username,
    get_user_improvement,
    initialize_database,
    save_result,
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-demo-secret-key")

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

initialize_database()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            return render_template("register.html", error="Please choose a username and password.")
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters long.")
        if get_user_by_username(username):
            return render_template("register.html", error="That username is already taken.")

        user_id = create_user(username, generate_password_hash(password))
        session["user_id"] = user_id
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/")
def index():
    if "user_id" in session:
        user_id = session["user_id"]
        return render_template(
            "index.html",
            summary=get_submission_summary(user_id),
            recent_submissions=get_recent_results(5, user_id),
            improvement=get_user_improvement(user_id),
            logged_in=True,
            username=session.get("username"),
        )

    return render_template(
        "index.html",
        summary=get_submission_summary(),
        recent_submissions=get_recent_results(5),
        improvement=None,
        logged_in=False,
        username=None,
    )


@app.route("/upload", methods=["GET"])
@login_required
def upload_page():
    return render_template(
        "upload.html",
        speaking_styles=SPEAKING_STYLES,
    )


@app.route("/overall")
@login_required
def overall():
    user_id = session["user_id"]
    return render_template(
        "overall.html",
        submissions=get_recent_results(user_id=user_id),
        summary=get_submission_summary(user_id),
        improvement=get_user_improvement(user_id),
    )


@app.route("/student/<int:submission_id>")
@login_required
def student(submission_id):
    submission = get_submission(submission_id, user_id=session["user_id"])
    if submission is None:
        return render_template("student.html", submission=None), 404
    style_key = submission.get("speaking_style")
    submission["speaking_style_label"] = SPEAKING_STYLES.get(
        style_key, {"label": style_key or "Not recorded"}
    )["label"]
    try:
        submission["score_breakdown"] = json.loads(submission.get("score_breakdown") or "{}")
    except (TypeError, ValueError):
        submission["score_breakdown"] = {}
    return render_template("student.html", submission=submission)


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    speaking_style = request.form.get("speaking_style", "")
    if speaking_style not in SPEAKING_STYLES:
        return render_template(
            "upload.html",
            speaking_styles=SPEAKING_STYLES,
            error="Choose a speaking style before analyzing the video."
        )

    uploaded_file = request.files.get("video")
    video_url = request.form.get("video_url", "").strip()

    if (uploaded_file is None or uploaded_file.filename == "") and not video_url:
        return render_template(
            "upload.html",
            speaking_styles=SPEAKING_STYLES,
            error="Please upload a video or enter a video URL."
        )

    if uploaded_file and uploaded_file.filename:
        filename = get_safe_filename(uploaded_file.filename)
        if not allowed_file(filename):
            return render_template(
                "upload.html",
                speaking_styles=SPEAKING_STYLES,
                error="Unsupported video format. Use MP4, MOV, AVI, MKV or WebM.",
            )
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(video_path)
        source = "Uploaded File"
    elif video_url:
        if not is_url(video_url):
            return render_template(
                "upload.html",
                speaking_styles=SPEAKING_STYLES,
                error="Please enter a valid HTTP/HTTPS URL."
            )
        try:
            video_path = download_video(video_url, UPLOAD_FOLDER)
            filename = os.path.basename(video_path)
            source = video_url
        except Exception as error:
            return render_template(
                "upload.html",
                speaking_styles=SPEAKING_STYLES,
                error=f"Video download failed: {error}"
            )

    try:
        audio_path = extract_audio(video_path, PROCESSED_FOLDER)
    except Exception as error:
        return render_template(
            "upload.html",
            speaking_styles=SPEAKING_STYLES,
            error=f"Audio extraction failed: {error}"
        )

    try:
        fluency_result = analyze_fluency(audio_path)
        fluency_data = {
            "wpm": fluency_result.get("words_per_minute", fluency_result.get("wpm", 0)),
            "filler_count": fluency_result.get("filler_words", fluency_result.get("filler_count", 0)),
            "pause_count": fluency_result.get("long_pauses", fluency_result.get("pause_count", 0)),
            "transcript": fluency_result.get("transcript", "")
        }
    except Exception as exc:
        print(f"Fluency analysis failed: {exc}")
        fluency_data = {
            "wpm": 0,
            "filler_count": 0,
            "pause_count": 0,
            "transcript": "Speech analysis unavailable."
        }

    try:
        audio_delivery_data = analyze_audio_delivery(audio_path)
    except Exception as exc:
        print(f"Audio delivery analysis failed: {exc}")
        audio_delivery_data = {
            "pitch_range_semitones": 0,
            "intensity_range_db": 0,
            "pause_ratio": 0,
            "long_pause_count": 0
        }

    visual_data = {
        "eye_contact_percentage": 0,
        "face_detected_ratio": 0
    }
    try:
        eye_result = analyze_eye_contact(video_path)
        visual_data["eye_contact_percentage"] = eye_result.get("eye_contact_percentage", 0)
    except Exception as exc:
        print(f"Eye contact analysis failed: {exc}")

    try:
        speaker_result = recognize_speaker(video_path)
        visual_data["face_detected_ratio"] = speaker_result.get("face_detected_ratio", 0)
    except Exception as exc:
        print(f"Face presence analysis failed: {exc}")

    processed_data = {
        "visual_metrics": visual_data,
        "fluency_metrics": fluency_data,
        "audio_delivery_metrics": audio_delivery_data,
        "speaking_style": speaking_style
    }

    score_result = calculate_scores(processed_data)
    final_score = score_result["total_score"]

    feedback = generate_feedback(processed_data, score_result["breakdown"])

    database_data = {
        "user_id": session["user_id"],
        "video_filename": filename,
        "video_source": source,
        "wpm": fluency_data["wpm"],
        "filler_count": fluency_data["filler_count"],
        "pause_count": fluency_data["pause_count"],
        "eye_contact_percentage": visual_data["eye_contact_percentage"],
        "face_detected_ratio": visual_data["face_detected_ratio"],
        "final_score": final_score,
        "transcript": fluency_data["transcript"],
        "speaking_style": speaking_style,
        "pitch_range_semitones": audio_delivery_data["pitch_range_semitones"],
        "intensity_range_db": audio_delivery_data["intensity_range_db"],
        "pause_ratio": audio_delivery_data["pause_ratio"],
        "long_pause_count": audio_delivery_data["long_pause_count"],
        "content_style_score": score_result["breakdown"]["content_style"],
        "vocal_delivery_score": score_result["breakdown"]["vocal_delivery"],
        "score_breakdown": score_result["breakdown"],
        "feedback": "\n".join(feedback),
    }

    submission_id = save_result(database_data)

    return render_template(
        "result.html",
        data=processed_data,
        score=final_score,
        score_breakdown=score_result["breakdown"],
        speaking_style=SPEAKING_STYLES[speaking_style]["label"],
        feedback=feedback,
        submission_id=submission_id,
        video_filename=filename,
        video_source=source,
        audio_path=audio_path,
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
