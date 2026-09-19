import argparse
import uuid
from pathlib import Path
from src.database import init_sqlite_db, register_video, update_video_metadata
from src.validator import validate_and_inspect_video
from src.preprocessor import extract_audio, sample_frames

def process_video_file(student_id: str, video_path_str: str):
    """Processes a single local video file through the offline input pipeline."""
    video_path = Path(video_path_str)
    
    if not video_path.exists():
        print(f"[Error] File not found: {video_path}")
        return

    video_id = f"vid_{uuid.uuid4().hex[:8]}"
    print(f"\n==========================================")
    print(f"Processing: {video_path.name}")
    print(f"Student ID: {student_id} | Internal Video ID: {video_id}")
    print(f"==========================================")

    # 1. Register in local SQLite DB
    seq_num = register_video(video_id, student_id, str(video_path))
    print(f"[DB] Registered video entry (Submission #{seq_num} for student {student_id})")

    try:
        # 2. Local Validation
        info = validate_and_inspect_video(video_path)
        print(f"[Validation] Duration: {info['duration']}s | FPS: {info['fps']} | Resolution: {info['resolution']}")

        # 3. Define output paths
        output_dir = Path(f"data/processed/{student_id}/{video_id}")
        audio_out = output_dir / "audio.wav"
        frames_out = output_dir / "frames"

        # 4. Offline Processing
        print("[Processing] Extracting 16kHz mono audio via FFmpeg...")
        extract_audio(video_path, audio_out)

        print("[Processing] Sampling frames (5 FPS) via OpenCV...")
        sample_frames(video_path, frames_out, target_fps=5)

        # 5. Update local database record
        update_video_metadata(video_id, {
            "audio_path": str(audio_out),
            "frames_dir": str(frames_out),
            "duration": info["duration"],
            "fps": info["fps"],
            "resolution": info["resolution"],
            "status": "READY_FOR_MODEL"
        })
        print(f"[Success] Data processed and stored at: {output_dir}\n")

    except Exception as e:
        print(f"[Error] Pipeline failed for {video_path.name}: {e}")
        update_video_metadata(video_id, {"status": "FAILED"})

if __name__ == "__main__":
    init_sqlite_db()

    parser = argparse.ArgumentParser(description="Offline Video Input Pipeline for Student Rating System")
    parser.add_argument("--student", type=str, required=True, help="Student Identifier (e.g., student_101)")
    parser.add_argument("--video", type=str, required=True, help="Path to local video file (e.g., data/raw/speech.mp4)")

    args = parser.parse_args()
    process_video_file(student_id=args.student, video_path_str=args.video)