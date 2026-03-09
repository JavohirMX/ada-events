from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, RSVP
from events.notifications import notify_event_reminder


class Command(BaseCommand):
    help = "Send in-app reminders for upcoming events"

    def add_arguments(self, parser):
        parser.add_argument("--hours-ahead", type=int, default=24)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--event-id", type=int)

    def handle(self, *args, **options):
        now = timezone.now()
        horizon = now + timedelta(hours=options["hours_ahead"])

        events = Event.objects.filter(
            event_date__gte=now.date(),
            event_date__lte=horizon.date(),
        )
        if options.get("event_id"):
            events = events.filter(pk=options["event_id"])

        created_for = 0
        scanned = 0
        for event in events:
            scanned += 1
            users = [
                r.user
                for r in RSVP.objects.filter(
                    event=event,
                    status__in=["going", "maybe"],
                ).select_related("user")
            ]
            if not options["dry_run"]:
                notify_event_reminder(event, users)
            created_for += len(users)

        self.stdout.write(
            self.style.SUCCESS(
                f"Reminders done. scanned_events={scanned} recipients={created_for} dry_run={options['dry_run']}"
            )
        )
