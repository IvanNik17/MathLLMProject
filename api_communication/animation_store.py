import json
import logging
import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from api_communication import config

log = logging.getLogger(__name__)

# Only names like these are ever served, so a URL can't reach other files
_SAFE_NAME = re.compile(r"^[A-Za-z0-9-]+\.mp4$")


@dataclass
class StoredFeedback:
    video_url: str
    explanation_text: str


class AnimationStore:

    def __init__(self, data_dir: Path):
        self.attempts_dir = data_dir / "videos" / "attempts"
        self.correct_dir = data_dir / "videos" / "correct"
        self.work_root = data_dir / "work"

        # Scratch folders left behind by a crash or restart are of no use
        shutil.rmtree(self.work_root, ignore_errors=True)

        for folder in (self.attempts_dir, self.correct_dir, self.work_root):
            folder.mkdir(parents=True, exist_ok=True)

    # --- Rendering scratch space --------------------------------------------

    def new_work_dir(self, attempt_id):
        folder = self.work_root / attempt_id
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def discard_work_dir(self, folder):
        shutil.rmtree(folder, ignore_errors=True)

    # --- Videos for single attempts -----------------------------------------

    def save_attempt_video(self, attempt_id, rendered_mp4: Path):
        """Moves a finished render into place. Returns its URL."""
        name = f"{attempt_id}.mp4"
        shutil.move(rendered_mp4, self.attempts_dir / name)
        return f"/api/videos/attempts/{name}"

    # --- Stored correct-answer feedback -------------------------------------

    @staticmethod
    def correct_key(problem):
        return f"p{problem.id}-{problem.fingerprint()}-v{config.ANIMATION_VERSION}"

    def find_correct(self, problem):
        """The stored feedback for a correct answer to this problem, or None"""
        key = self.correct_key(problem)
        video = self.correct_dir / f"{key}.mp4"
        info = self.correct_dir / f"{key}.json"

        if not (video.exists() and info.exists()):
            return None
        try:
            text = json.loads(info.read_text(encoding="utf-8"))["explanation_text"]
        except (OSError, ValueError, KeyError):
            return None

        info.touch()
        return StoredFeedback(video_url=f"/api/videos/correct/{key}.mp4", explanation_text=text)

    def save_correct(self, problem, rendered_mp4: Path, explanation_text):
        """Stores a correct-answer video and its feedback text, and returns the video URL"""
        key = self.correct_key(problem)
        video = self.correct_dir / f"{key}.mp4"
        info = self.correct_dir / f"{key}.json"

        # Move/write under a temporary name, then rename
        temporary_video = video.with_suffix(".mp4.tmp")
        shutil.move(rendered_mp4, temporary_video)
        os.replace(temporary_video, video)

        temporary_info = info.with_suffix(".json.tmp")
        temporary_info.write_text(
            json.dumps({
                "problem_id": problem.id,
                "equation": problem.equation_latex,
                "explanation_text": explanation_text,
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            }, indent=2),
            encoding="utf-8",
        )
        os.replace(temporary_info, info)

        return f"/api/videos/correct/{key}.mp4"

    # --- Serving ------------------------------------------------------------

    def video_path(self, kind, filename):
        """The file behind a /api/videos/<kind>/<filename> URL, or None."""
        folder = {"attempts": self.attempts_dir, "correct": self.correct_dir}.get(kind)
        if folder is None or not _SAFE_NAME.match(filename):
            return None
        path = folder / filename
        return path if path.is_file() else None

    # --- Cleaning up --------------------------------------------------------

    def cleanup(self, current_problems):
        """Deletes what is no longer needed. Safe to run at any time."""
        deleted = 0
        now = time.time()

        # 1. Attempt videos. First those that are too old, then the oldest beyond the storage limit
        attempt_videos = sorted(self.attempts_dir.glob("*.mp4"), key=_modified)
        max_age = config.ATTEMPT_VIDEO_HOURS * 3600
        keep = []
        for video in attempt_videos:
            if now - _modified(video) > max_age:
                deleted += _delete(video)
            else:
                keep.append(video)
        for video in keep[: max(0, len(keep) - config.MAX_ATTEMPT_VIDEOS)]:
            deleted += _delete(video)

        # 2. Correct-answer videos: those for problems that were edited or removed, then the least recently used beyond the storage limit
        valid_keys = {self.correct_key(p) for p in current_problems}
        infos = sorted(self.correct_dir.glob("*.json"), key=_modified)
        still_valid = []
        for info in infos:
            if info.stem in valid_keys:
                still_valid.append(info)
            else:
                deleted += _delete(info) + _delete(info.with_suffix(".mp4"))
        for info in still_valid[: max(0, len(still_valid) - config.MAX_CORRECT_VIDEOS)]:
            deleted += _delete(info) + _delete(info.with_suffix(".mp4"))

        # A video without its .json
        for video in self.correct_dir.glob("*.mp4"):
            if not video.with_suffix(".json").exists() and now - _modified(video) > 600:
                deleted += _delete(video)

        # 3. Scratch folders from renders that never finished
        for folder in self.work_root.iterdir():
            if now - _modified(folder) > 2 * config.RENDER_TIMEOUT_SECONDS:
                shutil.rmtree(folder, ignore_errors=True)
                deleted += 1

        if deleted:
            log.info("Cleanup deleted %d files", deleted)
        return deleted


def _modified(path):
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0


def _delete(path):
    try:
        path.unlink()
        return 1
    except FileNotFoundError:
        return 0
