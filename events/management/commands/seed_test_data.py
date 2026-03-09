import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, EventCategory, RSVP, Waitlist
from users.models import User


class Command(BaseCommand):
    help = "Seed test/demo users, events, RSVPs, and optional waitlist entries"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=20)
        parser.add_argument("--events", type=int, default=30)
        parser.add_argument("--rsvps-per-event", type=int, default=5)
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--seed", type=int, default=2026)

    def _ensure_categories(self):
        defaults = [
            ("Running", "running", "#10b981"),
            ("Beach", "beach", "#06b6d4"),
            ("Football", "football", "#f59e0b"),
            ("Hiking", "hiking", "#84cc16"),
            ("Food", "food", "#ef4444"),
            ("Workshop", "workshop", "#8b5cf6"),
            ("Social", "social", "#ec4899"),
            ("Other", "other", "#6b7280"),
        ]
        for name, icon, color in defaults:
            EventCategory.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "color": color},
            )

    def _reset_seeded(self):
        seeded_users = User.objects.filter(email__startswith="seed.user")
        Event.objects.filter(title__startswith="Seed Event").delete()
        seeded_users.delete()

    def _make_users(self, count):
        users = []
        for i in range(1, count + 1):
            email = f"seed.user{i}@example.com"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": f"seeduser{i}",
                    "password": "!",
                },
            )
            if not user.username:
                user.username = f"seeduser{i}"
                user.save(update_fields=["username"])
            users.append(user)
        return users

    def _make_events(self, users, count):
        categories = list(EventCategory.objects.all())
        events = []
        for i in range(1, count + 1):
            creator = random.choice(users)
            category = random.choice(categories) if categories else None
            date = timezone.now().date() + timedelta(days=random.randint(1, 40))
            event = Event.objects.create(
                creator=creator,
                title=f"Seed Event {i}",
                description=f"Demo event {i} for testing flows.",
                category=category,
                event_date=date,
                location=random.choice(
                    [
                        "Kuta Beach",
                        "Canggu Field",
                        "Seminyak",
                        "Ubud",
                        "Nusa Dua",
                    ]
                ),
                max_attendees=random.choice([None, 10, 15, 20]),
                is_public_attendees=random.choice([True, True, False]),
            )
            events.append(event)
        return events

    def _seed_rsvps(self, events, users, per_event):
        statuses = ["going", "maybe", "not_going"]
        total = 0
        for event in events:
            sample = random.sample(users, k=min(per_event, len(users)))
            for user in sample:
                RSVP.objects.update_or_create(
                    event=event,
                    user=user,
                    defaults={"status": random.choice(statuses)},
                )
                total += 1

            if (
                event.max_attendees
                and event.rsvps.filter(status="going").count() >= event.max_attendees
            ):
                overflow = [
                    u
                    for u in users
                    if not RSVP.objects.filter(event=event, user=u).exists()
                ][:2]
                for idx, user in enumerate(overflow, start=1):
                    Waitlist.objects.get_or_create(
                        event=event, user=user, defaults={"position": idx}
                    )
        return total

    def handle(self, *args, **options):
        random.seed(options["seed"])
        self._ensure_categories()

        if options["reset"]:
            self._reset_seeded()
            self.stdout.write("Removed existing seeded data")

        users = self._make_users(options["users"])
        events = self._make_events(users, options["events"])
        rsvps = self._seed_rsvps(events, users, options["rsvps_per_event"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded test data: users={len(users)} events={len(events)} rsvps={rsvps}"
            )
        )
