
import os
from pathlib import Path

from dotenv import load_dotenv

# The folder that holds api_communication/, math_helper/ and so on. Paths are built from here so the server works no matter which folder it is started in.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def _int(name, default):
    return int(os.environ.get(name, default))


def _path(name, default):
    path = Path(os.environ.get(name, default))
    return path if path.is_absolute() else PROJECT_ROOT / path


# --- The language model -----------------------------------------------------
LLM_BASE_URL = os.environ.get("MATHLLM_LLM_BASE_URL", "https://app-mathllm.cloud.sdu.dk/api")
LLM_API_KEY = os.environ.get("MATHLLM_API_KEY", "")
LLM_MODEL = os.environ.get("MATHLLM_LLM_MODEL", "mistral:latest")
# Seconds to wait for the model
LLM_TIMEOUT_SECONDS = _int("MATHLLM_LLM_TIMEOUT", 60)

# --- Files ------------------------------------------------------------------
PROBLEMS_FILE = _path("MATHLLM_PROBLEMS_FILE", "content/problems.json")
# Everything the server writes
DATA_DIR = _path("MATHLLM_DATA_DIR", "data")

# --- How much work runs at once ---------------------------------------------
# Manim uses one CPU core per render, and a render takes 10-60 seconds.
MAX_PARALLEL_RENDERS = _int("MATHLLM_MAX_PARALLEL_RENDERS", 2)
# Calls to the language model mostly wait on the network, so more can overlap.
MAX_PARALLEL_LLM_CALLS = _int("MATHLLM_MAX_PARALLEL_LLM_CALLS", 6)
MAX_UNFINISHED_ATTEMPTS = _int("MATHLLM_MAX_UNFINISHED_ATTEMPTS", 40)
RENDER_TIMEOUT_SECONDS = _int("MATHLLM_RENDER_TIMEOUT", 300)

# --- Cleaning up ------------------------------------------------------------
ATTEMPT_VIDEO_HOURS = _int("MATHLLM_ATTEMPT_VIDEO_HOURS", 6)
MAX_ATTEMPT_VIDEOS = _int("MATHLLM_MAX_ATTEMPT_VIDEOS", 300)
MAX_CORRECT_VIDEOS = _int("MATHLLM_MAX_CORRECT_VIDEOS", 200)
CLEANUP_EVERY_MINUTES = _int("MATHLLM_CLEANUP_EVERY_MINUTES", 10)

# Change this number after editing a scene or the feedback prompt. Every stored correct-answer video is then made fresh on next use.
ANIMATION_VERSION = 1
