"""
Background task definitions for event reminders.

Scheduled via: python manage.py schedule_reminders
Executed by:   python manage.py qcluster  (django-q2)
"""

from datetime import timedelta

from django.utils import timezone

from events.models import Event, RSVP
from events.notifications import notify_event_reminder


def send_24h_reminders():
    """Send in-app reminders to RSVPs for events starting in ~24 hours."""
    _send_reminders(hours_ahead=24)


def send_1h_reminders():
    """Send in-app reminders to RSVPs for events starting in ~1 hour."""
    _send_reminders(hours_ahead=1)


def _send_reminders(hours_ahead: int):
    now = timezone.now()
    horizon = now + timedelta(hours=hours_ahead)

    events = Event.objects.filter(
        event_date__gte=now.date(),
        event_date__lte=horizon.date(),
    )

    for event in events:
        recipients = [
            r.user
            for r in RSVP.objects.filter(
                event=event,
                status__in=["going", "maybe"],
            ).select_related("user")
        ]
        if recipients:
            notify_event_reminder(event, recipients)
