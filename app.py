import json
import os
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import EVALUATORS, PROGRAM_WEEKS, RUBRIC
from db import has_submitted, init_db
from ext_summary import run_ext_summaries
from weekly_update import post_weekly_update
from calendar_walker import check_calendars
from scheduler import start_scheduler

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_current_week():
    """Return the active program week, or fall back to CURRENT_WEEK env var."""
    override = os.getenv("CURRENT_WEEK")
    if override:
        return int(override)
    today = date.today()
    for week, end_str in PROGRAM_WEEKS.items():
        if today <= date.fromisoformat(end_str):
            return week
    return 4


def find_evaluator_by_slack_id(user_id: str):
    for key, ev in EVALUATORS.items():
        if ev["slack_user_id"] == user_id:
            return key, ev
    return None, None


# ── Weekly reminder ───────────────────────────────────────────────────────────

def post_weekly_reminder():
    """
    Every Thursday 4 PM ET — post a targeted reminder in each Spark thread
    where feedback is still missing, tagging only the mentors who haven't submitted.
    """
    threads_file = os.path.join(os.path.dirname(__file__), "spark_threads.json")
    if not os.path.exists(threads_file):
        print("[reminder] spark_threads.json not found — run post_spark_threads.py first")
        return

    with open(threads_file) as f:
        threads = json.load(f)

    week = get_current_week()

    for spark_name, info in threads.items():
        missing = []
        for ev_key, ev in EVALUATORS.items():
            if spark_name not in ev["assigned_sparks"]:
                continue
            if not RUBRIC[week][ev["section"]]:
                continue
            if ev["slack_user_id"].startswith("PLACEHOLDER"):
                continue
            if not has_submitted(week, spark_name, ev_key):
                missing.append(ev["slack_user_id"])

        if not missing:
            print(f"[reminder] {spark_name} — all feedback submitted, skipping")
            continue

        tags = " ".join(f"<@{uid}>" for uid in missing)
        text = (
            f":bell: *Week {week} feedback reminder* — {tags} we're still waiting on "
            f"your notes for *{spark_name}* this week. Drop them here when you get a chance! :sparkles:"
        )

        try:
            app.client.chat_postMessage(
                channel=info["channel"],
                thread_ts=info["ts"],
                text=text,
            )
            print(f"[reminder] Posted reminder in {spark_name} thread ({len(missing)} missing)")
        except Exception as e:
            print(f"[reminder] Error posting to {spark_name} thread: {e}")


# ── Health server ─────────────────────────────────────────────────────────────

class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silence access logs


def _start_health_server():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Health server listening on port {port}")


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _start_health_server()
    init_db()

    start_scheduler(
        post_reminder_fn=post_weekly_reminder,
        post_ext_summaries_fn=run_ext_summaries,
        post_weekly_update_fn=post_weekly_update,
        check_calendars_fn=check_calendars,
        get_week_fn=get_current_week,
    )

    print("SparkBot running in Socket Mode.")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
