"""
Registers periodic background tasks for event reminders using django-q2.

Run once after deploy (or whenever you want to reschedule):
    python manage.py schedule_reminders

Tasks are executed by the qcluster worker:
    python manage.py qcluster
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Register periodic background tasks for event reminders (django-q2)"

    def handle(self, *args, **options):
        from django_q.models import Schedule

        task_configs = [
            {
                "name": "send_24h_reminders",
                "func": "events.tasks.send_24h_reminders",
            },
            {
                "name": "send_1h_reminders",
                "func": "events.tasks.send_1h_reminders",
            },
        ]

        for config in task_configs:
            _, created = Schedule.objects.update_or_create(
                name=config["name"],
                defaults={
                    "func": config["func"],
                    "schedule_type": Schedule.HOURLY,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(
                f"{action} schedule: {config['name']} (hourly)"
            ))
