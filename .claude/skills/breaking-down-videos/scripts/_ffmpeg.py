"""Make sure ffmpeg and ffprobe are on PATH. Uses the system copy if there is one, otherwise
the static build the static-ffmpeg package downloads once (about 70 MB)."""
import shutil


def ensure():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    import static_ffmpeg
    static_ffmpeg.add_paths()
