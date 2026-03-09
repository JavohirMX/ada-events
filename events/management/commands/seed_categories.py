from django.core.management.base import BaseCommand
from events.models import EventCategory

# Icon names from https://lucide.dev — rendered via the Lucide CDN loaded in base.html
CATEGORIES = [
    {"name": "Running",  "icon": "activity",   "color": "#10b981"},
    {"name": "Beach",    "icon": "waves",       "color": "#06b6d4"},
    {"name": "Football", "icon": "circle-dot",  "color": "#f59e0b"},
    {"name": "Hiking",   "icon": "mountain",    "color": "#84cc16"},
    {"name": "Food",     "icon": "utensils",    "color": "#ef4444"},
    {"name": "Workshop", "icon": "hammer",      "color": "#8b5cf6"},
    {"name": "Social",   "icon": "users",       "color": "#ec4899"},
    {"name": "Travel",   "icon": "plane",       "color": "#3b82f6"},
    {"name": "Other",    "icon": "calendar",    "color": "#6b7280"},
]

class Command(BaseCommand):
    help = "Seed event categories with SVG icons"

    def handle(self, *args, **options):
        for cat_data in CATEGORIES:
            cat, created = EventCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "icon": cat_data["icon"],
                    "color": cat_data["color"],
                },
            )
            if not created:
                cat.icon = cat_data["icon"]
                cat.color = cat_data["color"]
                cat.save(update_fields=["icon", "color"])
                self.stdout.write(f"Updated category: {cat.name}")
            else:
                self.stdout.write(f"Created category: {cat.name}")

        self.stdout.write(self.style.SUCCESS("Seeded event categories with SVG icons"))
