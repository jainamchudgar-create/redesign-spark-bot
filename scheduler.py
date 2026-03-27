"""
Scheduler:
  - Every 10 min          → check mentor calendars for ended Spark calls → nudge in thread
  - Wednesday 9 AM ET (14:00 UTC) → post ext channel summaries to all Spark threads
  - Thursday 4 PM ET (21:00 UTC)  → post targeted reminders where feedback is missing
  - Friday 4 PM ET (21:00 UTC)    → post weekly status update to #proj-redesign-spark
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


def start_scheduler(post_reminder_fn, post_ext_summaries_fn, post_weekly_update_fn,
                    check_calendars_fn, get_week_fn):
    scheduler = BackgroundScheduler()

    # Every 10 minutes — calendar poll for post-call nudges
    scheduler.add_job(
        check_calendars_fn,
        IntervalTrigger(minutes=10),
        id="calendar_poll",
        replace_existing=True,
    )

    # Wednesday 9 AM ET (14:00 UTC) — ext channel summaries to each Spark thread
    scheduler.add_job(
        post_ext_summaries_fn,
        CronTrigger(day_of_week="wed", hour=14, minute=0, timezone="UTC"),
        id="wednesday_ext_summaries",
        replace_existing=True,
    )

    # Thursday 4 PM ET (21:00 UTC) — reminder in threads where feedback is missing
    scheduler.add_job(
        post_reminder_fn,
        CronTrigger(day_of_week="thu", hour=21, minute=0, timezone="UTC"),
        id="weekly_thread_reminder",
        replace_existing=True,
    )

    # Friday 4 PM ET (21:00 UTC) — weekly status update to main channel
    scheduler.add_job(
        lambda: post_weekly_update_fn(get_week_fn()),
        CronTrigger(day_of_week="fri", hour=21, minute=0, timezone="UTC"),
        id="friday_weekly_update",
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler started:")
    print("  Every 10 min      → calendar poll for post-call nudges")
    print("  Wed 9 AM ET       → ext channel summaries to Spark threads")
    print("  Thu 4 PM ET       → feedback reminders (missing only)")
    print("  Fri 4 PM ET       → weekly status update to #proj-redesign-spark")
    return scheduler
