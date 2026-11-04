# Starts and stops the server in a tmux session, so it keeps running after we close VS Code. Run it inside the container.
#
#   bash deploy/run.sh start      start the server (does nothing if it's running)
#   bash deploy/run.sh stop       stop it
#   bash deploy/run.sh restart    stop, then start (after a git pull, for example)
#   bash deploy/run.sh status     is it running, and does it answer?
#   bash deploy/run.sh logs       follow the log (Ctrl+C stops watching, not the server)
#   bash deploy/run.sh attach     look at the live tmux window (to leave: press and release Ctrl+B, then press D)
#

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION="mathwiz"
PORT="${MATHWIZ_PORT:-10100}"
LOG="$ROOT/data/server.log"
PY="$ROOT/.venv/bin/python"

is_running() {
    tmux has-session -t "$SESSION" 2>/dev/null
}

answers() {
    curl -fsS --max-time 3 "http://127.0.0.1:$PORT/api/health" 2>/dev/null
}

check_ready_to_start() {
    local ok=1
    if [[ ! -x "$PY" ]]; then
        echo "No Python environment at .venv."
        ok=0
    fi
    if ! grep -qE '^MATHLLM_API_KEY=.+' "$ROOT/.env" 2>/dev/null; then
        echo "No MATHLLM_API_KEY in .env."
        ok=0
    fi
    if [[ ! -f "$ROOT/frontend/dist/index.html" ]]; then
        echo "Warning: no built frontend (frontend/dist). The API will run, but the page won't load."
    fi
    [[ $ok == 1 ]]
}

start() {
    if is_running; then
        echo "Already running. Use 'restart' to restart it."
        return 0
    fi
    check_ready_to_start || exit 1
    mkdir -p "$ROOT/data"

    # The loop restarts the server if it crashes, after a pause so a server that crashes straight away doesn't spin.
    tmux new-session -d -s "$SESSION" -c "$ROOT" bash -c "
        while true; do
            echo \"=== starting \$(date '+%F %T') ===\"
            '$PY' -m uvicorn api_communication.api_server:app --host 0.0.0.0 --port $PORT
            echo \"=== server exited with code \$? at \$(date '+%F %T'); restarting in 5 s ===\"
            sleep 5
        done 2>&1 | tee -a '$LOG'
    "

    echo -n "Starting"
    for _ in $(seq 1 30); do
        if answers >/dev/null; then
            echo " - up on port $PORT."
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo
    echo "Started, but it doesn't answer yet. The last lines of the log:"
    tail -n 20 "$LOG"
    exit 1
}

stop() {
    if is_running; then
        tmux kill-session -t "$SESSION"
        echo "Stopped."
    else
        echo "Not running."
    fi
}

status() {
    if is_running; then
        echo "tmux session: running"
    else
        echo "tmux session: not running"
    fi
    local health
    if health="$(answers)"; then
        echo "Answers on port $PORT: $health"
    else
        echo "Nothing answers on port $PORT."
    fi
}

case "${1:-}" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; start ;;
    status)  status ;;
    logs)    touch "$LOG"; tail -n 50 -f "$LOG" ;;
    attach)  tmux attach -t "$SESSION" ;;
    *)
        sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
        exit 1
        ;;
esac
