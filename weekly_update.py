"""
Feature 4: Every Friday, post a Week N status update to #proj-redesign-spark
showing all 8 Sparks, their CV mentor feedback status, and what's happening.
"""
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

from config import ALL_SPARKS, EVALUATORS
from db import has_nudged, record_nudge
from slack_client import get_thread_replies, post_message

THREADS_FILE = os.path.join(os.path.dirname(__file__), "spark_threads.json")
SUMMARY_CHANNEL = os.environ.get("SUMMARY_CHANNEL_ID", "C0A3P3Z55GQ")
SPARKBOT_USER_ID = "U0AP3776CM6"

# Sarah Cranston — always CC'd
SARAH_USER_ID = "U026G26GK38"

CV_MENTOR_IDS = {
    ev["slack_user_id"]
    for ev in EVALUATORS.values()
    if ev["section"] == "concept_vision"
}


def _cv_mentors_for_spark(spark_name):
    """Return list of (key, ev) for CV mentors assigned to this Spark."""
    return [
        (key, ev) for key, ev in EVALUATORS.items()
        if ev["section"] == "concept_vision"
        and spark_name in ev["assigned_sparks"]
        and not ev["slack_user_id"].startswith("PLACEHOLDER")
    ]


def _get_cv_feedback_status(spark_name, thread_replies):
    """
    Returns (has_feedback: bool, who_posted: list[str], missing: list[str])
    """
    cv_mentors = _cv_mentors_for_spark(spark_name)
    poster_ids = {
        m.get("user") for m in thread_replies
        if m.get("user") in CV_MENTOR_IDS
        and m.get("user") != SPARKBOT_USER_ID
    }
    who_posted = [ev["name"] for _, ev in cv_mentors if ev["slack_user_id"] in poster_ids]
    missing_ids = [ev["slack_user_id"] for _, ev in cv_mentors if ev["slack_user_id"] not in poster_ids]
    has_feedback = len(who_posted) > 0
    return has_feedback, who_posted, missing_ids


def _get_latest_cv_feedback_text(thread_replies):
    """Extract the most recent CV mentor feedback message text (truncated)."""
    for msg in thread_replies:
        uid = msg.get("user", "")
        if uid in CV_MENTOR_IDS and uid != SPARKBOT_USER_ID:
            text = msg.get("text", "").strip()
            if text and len(text) > 20:
                # truncate to ~120 chars
                return text[:120] + ("..." if len(text) > 120 else "")
    return None


def _cv_mentor_names_for_spark(spark_name):
    """Return display names of CV mentors for this Spark."""
    return [ev["name"] for _, ev in _cv_mentors_for_spark(spark_name)]


def build_weekly_update(week):
    """Build the full weekly update message text."""
    with open(THREADS_FILE) as f:
        threads = json.load(f)

    rows = []
    all_missing = {}  # spark_name -> list of missing user_ids

    for spark_name in ALL_SPARKS:
        info = threads.get(spark_name)
        if not info:
            continue

        replies = get_thread_replies(info["channel"], info["ts"])
        has_feedback, who_posted, missing_ids = _get_cv_feedback_status(spark_name, replies)
        cv_names = _cv_mentor_names_for_spark(spark_name)
        snippet = _get_latest_cv_feedback_text(replies) if has_feedback else None

        rows.append({
            "spark_name": spark_name,
            "cv_mentors": ", ".join(cv_names),
            "has_feedback": has_feedback,
            "who_posted": who_posted,
            "missing_ids": missing_ids,
            "snippet": snippet,
        })

        if missing_ids:
            all_missing[spark_name] = missing_ids

    # Build message
    date_str = datetime.utcnow().strftime("%B %d")
    lines = [
        f":bar_chart: *SparkBot — Week {week} Status Update*",
        f"Here's where all {len(ALL_SPARKS)} Sparks stand this week. Concept Vision mentors: please drop your notes in the thread if you haven't yet!\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for row in rows:
        flag = "✅" if row["has_feedback"] else "🚨"
        feedback_label = f"✅ {', '.join(row['who_posted'])} posted" if row["has_feedback"] else "❌ No feedback yet"
        first_name = row["spark_name"].split()[0]
        lines.append(f"\n{flag} *{row['spark_name']}* | {row['cv_mentors']} | {feedback_label}")
        if row["snippet"]:
            lines.append(f"> _{row['snippet']}_")

    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Bell line — only tag missing mentors
    if all_missing:
        bell_parts = []
        seen_ids = set()
        for spark_name, missing_ids in all_missing.items():
            for uid in missing_ids:
                if uid not in seen_ids:
                    seen_ids.add(uid)
            tags = " ".join(f"<@{uid}>" for uid in missing_ids)
            first_name = spark_name.split()[0]
            bell_parts.append(f"{tags} for {first_name}'s thread")
        lines.append(f"\n:bell: Still waiting on notes — {', '.join(bell_parts)}. Even 3 bullets helps! :sparkles:")

    lines.append(f"\ncc <@{SARAH_USER_ID}>")

    return "\n".join(lines)


def post_weekly_update(week):
    """Generate and post the weekly status update to the main channel."""
    nudge_key = f"weekly_update_w{week}"
    if has_nudged(nudge_key, "main_channel"):
        logger.info("Weekly update for week %d already posted, skipping.", week)
        return

    logger.info("Building Week %d status update...", week)
    text = build_weekly_update(week)
    result = post_message(SUMMARY_CHANNEL, text)
    if result.get("ok"):
        record_nudge(nudge_key, "main_channel")
        logger.info("Posted Week %d status update.", week)
    else:
        logger.error("Failed to post Week %d status update: %s", week, result.get("error"))
