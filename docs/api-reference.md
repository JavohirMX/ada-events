# API Reference

## Table of Contents

1. [Models](#models)
2. [Views](#views)
3. [URLs](#urls)
4. [Templates](#templates)
5. [Management Commands](#management-commands)

---

## Models

### User

Extends Django's AbstractUser with additional fields.

```python
from users.models import User

user = User.objects.create_user(
    username="john",
    email="john@example.com",
    password="password123",
    bio="iOS Developer",
    whatsapp_link="https://wa.me/1234567890"
)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `username` | CharField | Unique username |
| `email` | EmailField | Unique email (required) |
| `bio` | TextField | User biography |
| `profile_photo` | ImageField | Profile picture |
| `whatsapp_link` | URLField | WhatsApp contact link |
| `date_joined` | DateTimeField | Account creation date |

---

### Event

Main event model.

```python
from events.models import Event, EventCategory

# Create event
event = Event.objects.create(
    creator=user,
    title="Morning Run at Kuta Beach",
    description="Let's run together!",
    category=EventCategory.objects.get(name="Running"),
    event_date="2026-03-15",
    event_time="06:00:00",
    location="Kuta Beach, Bali",
    location_url="https://maps.google.com/...",
    max_attendees=20,
    is_public_attendees=True,
    whatsapp_group_link="https://chat.whatsapp.com/..."
)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `creator` | ForeignKey | Event creator (User) |
| `title` | CharField | Event title (max 200) |
| `description` | TextField | Event description |
| `category` | ForeignKey | Event category |
| `event_date` | DateField | Event date |
| `event_time` | TimeField | Event time (optional) |
| `location` | CharField | Location name |
| `location_url` | URLField | Google Maps link |
| `image` | ImageField | Cover image |
| `attachments` | FileField | Event files |
| `is_public_attendees` | BooleanField | Show attendee list |
| `max_attendees` | PositiveIntegerField | Max attendees |
| `whatsapp_group_link` | URLField | WhatsApp group |
| `gallery_link` | URLField | Photo album link |
| `created_at` | DateTimeField | Creation timestamp |
| `updated_at` | DateTimeField | Last update |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `is_upcoming` | bool | Event hasn't occurred yet |
| `is_past` | bool | Event has occurred |
| `attendee_count` | int | Number of "going" RSVPs |
| `is_full` | bool | At max capacity |
| `can_edit_gallery` | bool | Can edit gallery (after event) |

---

### EventCategory

Predefined event categories.

```python
# Default categories
categories = EventCategory.objects.all()
# - Running
# - Beach
# - Football
# - Hiking
# - Food
# - Workshop
# - Social
# - Other
```

---

### RSVP

Event attendance tracking.

```python
from events.models import RSVP

# Create RSVP
rsvp = RSVP.objects.create(
    event=event,
    user=user,
    status="going"  # "going", "maybe", "not_going"
)

# Update RSVP
rsvp.status = "maybe"
rsvp.save()
```

**Status Options:**

| Status | Description |
|--------|-------------|
| `going` | User will attend |
| `maybe` | User might attend |
| `not_going` | User cannot attend |

---

### Waitlist

When events reach capacity.

```python
from events.models import Waitlist

# Add to waitlist
waitlist = Waitlist.objects.create(
    event=event,
    user=user,
    position=1
)
```

Behavior in app flow:
- `going` RSVP is added to waitlist when capacity is full.
- Waitlist is FIFO.
- Next waitlisted user is promoted automatically when a `going` attendee leaves.

---

### Notification

In-app notifications.

```python
from events.models import Notification

notification = Notification.objects.create(
    user=user,
    notification_type="event_created",
    message="New event: Beach Trip",
    link="/events/1/"
)
```

---

## Views

### Home View

**URL:** `/`

Displays upcoming events on homepage.

```python
# In views.py
def home(request):
    upcoming_events = Event.objects.filter(
        event_date__gte=timezone.now().date()
    ).order_by("event_date", "event_time")[:6]
    return render(request, "events/home.html", {
        "upcoming_events": upcoming_events
    })
```

---

### Event List

**URL:** `/events/`

List all upcoming events with optional filtering.

```python
# Query parameters
/events/?category=Running
/events/?q=beach
/events/?category=Running&q=kuta
```

---

### Event Detail

**URL:** `/events/<pk>/`

Full event details with RSVP form.

---

### Event Create

**URL:** `/events/create/` (requires login)

Create new event form.

---

### Event Edit

**URL:** `/events/<pk>/edit/` (creator only)

Edit existing event.

---

### RSVP

**URL:** `/events/<pk>/rsvp/` (POST only, requires login)

Submit RSVP response.

Capacity behavior:
- available slot: RSVP becomes `going`
- full event + `going`: user is waitlisted
- attendee leaves: next waitlisted user promoted to `going`

**Form Data:**
```html
<form action="/events/1/rsvp/" method="post">
    {% csrf_token %}
    <button name="status" value="going">Going</button>
    <button name="status" value="maybe">Maybe</button>
    <button name="status" value="not_going">Can't Go</button>
</form>
```

---

### Calendar (.ics)

**URL:** `/events/<pk>/calendar.ics/`

Download iCalendar file for event.

---

### User Profile

**URL:** `/users/profile/<username>/` (requires login)

View user profile.

### User Profile Edit

**URL:** `/users/profile/edit/` (requires login)

Edit current user's profile fields:
- `username`
- `bio`
- `whatsapp_link`
- `profile_photo`

---

### User Dashboard

**URL:** `/users/dashboard/` (requires login)

User's events and RSVPs.

### Notifications Inbox

**URLs:**
- `/users/notifications/`
- `/users/notifications/<pk>/read/` (POST)
- `/users/notifications/read-all/` (POST)

Features:
- unread/read states
- mark single or all notifications read

---

### Past Events

**URL:** `/past/`

Archive of past events.

---

## URLs

### Root URLs (`ada_events/urls.py`)

```python
urlpatterns = [
    path("", event_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("users/", include("users.urls", namespace="users")),
    path("", include("events.urls", namespace="events")),
]
```

### User URLs (`users/urls.py`)

```python
app_name = "users"

urlpatterns = [
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notifications_inbox, name="notifications_inbox"),
    path("notifications/<int:pk>/read/", views.notification_mark_read, name="notification_mark_read"),
    path("notifications/read-all/", views.notifications_mark_all_read, name="notifications_mark_all_read"),
]
```

### Event URLs (`events/urls.py`)

```python
app_name = "events"

urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/rsvp/", views.rsvp, name="rsvp"),
    path("events/<int:pk>/calendar.ics/", views.event_ics, name="event_ics"),
    path("past/", views.past_events, name="past_events"),
]
```

---

## Templates

### Template Hierarchy

```
templates/
└── base.html              # Base template with nav/footer
    └── events/
        ├── home.html      # Homepage
        ├── event_list.html
        ├── event_detail.html
        ├── event_create.html
        ├── event_edit.html
        └── past_events.html
    └── users/
        ├── profile.html
        └── dashboard.html
```

### Context Variables

**home.html:**
```python
{
    "upcoming_events": QuerySet[Event]
}
```

**event_list.html:**
```python
{
    "events": QuerySet[Event],
    "categories": QuerySet[EventCategory],
    "selected_category": str,
    "search_query": str,
}
```

**event_detail.html:**
```python
{
    "event": Event,
    "user_rsvp": RSVP | None,
    "attendees": QuerySet[RSVP]
}
```

---

## Management Commands

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Django Shell

```bash
python manage.py shell
```

### Check System

```bash
python manage.py check
```

### Seed Categories

```bash
python manage.py seed_categories
```

### Send Event Reminders

```bash
python manage.py send_event_reminders --dry-run
python manage.py send_event_reminders --hours-ahead 24
python manage.py send_event_reminders --event-id 12
```

### Seed Test Data

```bash
python manage.py seed_test_data --users 20 --events 30 --rsvps-per-event 5
python manage.py seed_test_data --reset --users 10 --events 12
```

Options:
- `--users`: number of seeded users
- `--events`: number of seeded events
- `--rsvps-per-event`: RSVP density per event
- `--reset`: delete prior seeded records before re-seeding
- `--seed`: deterministic random seed value

---

## Notifications + Reminders

- Notifications are generated from view/service layer on event create/update and RSVP.
- Reminder notifications are generated by `send_event_reminders` command.
