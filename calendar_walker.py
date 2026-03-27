"""
Feature 1 & 2: Poll mentor Google Calendars every 10 minutes.
When a call with a Spark is detected as just ended, post a nudge in the
Spark's thread on #proj-redesign-spark tagging the mentor(s) on the call.

REQUIRES: Google service account with domain-wide delegation.
IT setup needed:
  1. Go to Google Workspace Admin Console → Security → API Controls → Domain-wide Delegation
  2. Add the service account client ID with scope:
     https://www.googleapis.com/auth/calendar.readonly
  3. Set GOOGLE_IMPERSONATE_USER env var to any RH admin email (e.g. jainam.chudgar@redesignhealth.com)
     — the service account will impersonate this user to access other calendars.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import EVALUATORS
from db import has_nudged, record_nudge
from slack_client import post_message

THREADS_FILE = os.path.join(os.path.dirname(__file__), "spark_threads.json")

CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"

# How long after a call ends before we post the nudge (seconds)
NUDGE_DELAY_SECONDS = 15 * 60  # 15 minutes

# Only check events that ended within this window (to catch recent calls)
LOOKBACK_MINUTES = 30


def _get_calendar_service(impersonate_email):
    """Build a Google Calendar API client impersonating a specific user."""
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(
            info,
            scopes=[CALENDAR_SCOPE],
            subject=impersonate_email,
        )
    else:
        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=[CALENDAR_SCOPE],
            subject=impersonate_email,
        )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _load_sparks():
    with open(THREADS_FILE) as f:
        return json.load(f)


def _event_matches_spark(event, spark_info, spark_name):
    """
    Check if a calendar event is a call with this Spark.
    Matches on: event title keywords OR attendee email.
    """
    title = event.get("summary", "").lower()
    keywords = spark_info.get("keywords", [spark_name.split()[0].lower()])
    spark_email = spark_info.get("email", "").lower()

    # Check title
    for kw in keywords:
        if kw.lower() in title:
            return True

    # Check attendees
    for attendee in event.get("attendees", []):
        email = attendee.get("email", "").lower()
        if spark_email and email == spark_email:
            return True

    return False


def _get_recently_ended_events(service, mentor_email):
    """
    Fetch events from the mentor's calendar that ended in the last LOOKBACK_MINUTES.
    """
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(minutes=LOOKBACK_MINUTES)).isoformat()
    time_max = now.isoformat()

    try:
        result = service.events().list(
            calendarId=mentor_email,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return result.get("items", [])
    except Exception as e:
        print(f"[calendar] Error fetching events for {mentor_email}: {e}")
        return []


def _post_nudge(spark_name, spark_info, mentor_user_ids, event_summary):
    """Post a nudge in the Spark's thread tagging the relevant mentors."""
    tags = " ".join(f"<@{uid}>" for uid in mentor_user_ids)
    text = (
        f":calendar: Hey {tags} — looks like you just finished a call with *{spark_name}*!\n\n"
        f"Drop your observations here when you're ready — what's landing, what's still fuzzy, "
        f"any flags on concept or direction. Even 3 bullets helps. :sparkles:"
    )
    post_message(spark_info["channel"], text, thread_ts=spark_info["ts"])
    print(f"[calendar] Posted nudge for {spark_name} (mentors: {mentor_user_ids})")


def check_calendars():
    """
    Main polling function — called every 10 minutes by the scheduler.
    Checks all CV mentor calendars for recently ended Spark calls.
    """
    impersonate_user = os.getenv("GOOGLE_IMPERSONATE_USER")
    if not impersonate_user:
        print("[calendar] GOOGLE_IMPERSONATE_USER not set — skipping calendar check")
        return

    sparks = _load_sparks()
    now = datetime.now(timezone.utc)

    # Group CV mentors by their assigned sparks
    cv_mentors = {
        key: ev for key, ev in EVALUATORS.items()
        if ev["section"] == "concept_vision"
        and not ev.get("email", "").startswith("PLACEHOLDER")
        and "email" in ev
    }

    # For each CV mentor, check their calendar
    for ev_key, ev in cv_mentors.items():
        mentor_email = ev["email"]
        try:
            service = _get_calendar_service(mentor_email)
            events = _get_recently_ended_events(service, mentor_email)
        except Exception as e:
            print(f"[calendar] Could not access calendar for {mentor_email}: {e}")
            continue

        for event in events:
            event_id = event.get("id", "")
            end_str = event.get("end", {}).get("dateTime")
            if not end_str:
                continue  # skip all-day events

            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            minutes_since_end = (now - end_time).total_seconds() / 60

            # Only nudge if ended 13-17 minutes ago (15 min window)
            if not (13 <= minutes_since_end <= 17):
                continue

            # Check which assigned Sparks this event matches
            for spark_name, spark_info in sparks.items():
                if spark_name not in ev["assigned_sparks"]:
                    continue
                if not _event_matches_spark(event, spark_info, spark_name):
                    continue
                if has_nudged(event_id, spark_name):
                    continue

                # Find all mentors on this event from our known mentors
                attendee_emails = {
                    a.get("email", "").lower()
                    for a in event.get("attendees", [])
                }
                mentor_user_ids = [
                    m["slack_user_id"]
                    for m in cv_mentors.values()
                    if m["email"].lower() in attendee_emails
                    and spark_name in m["assigned_sparks"]
                ] or [ev["slack_user_id"]]  # fallback to just this mentor

                _post_nudge(spark_name, spark_info, mentor_user_ids, event.get("summary", ""))
                record_nudge(event_id, spark_name)

        time.sleep(0.5)  # avoid hitting rate limits
