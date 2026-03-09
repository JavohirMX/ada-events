import pytest
from django.utils import timezone
from datetime import timedelta, datetime
from users.models import User
from events.models import Event, EventCategory


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="password"
    )


@pytest.fixture
def category():
    return EventCategory.objects.create(name="Conference", icon="mic", color="#FF0000")


@pytest.fixture
def event_data(user, category):
    return {
        "creator": user,
        "title": "Test Event",
        "description": "This is a test event",
        "category": category,
        "event_date": timezone.now().date() + timedelta(days=7),
        "event_time": timezone.now().time(),
        "location": "Test Location",
        "is_public_attendees": True,
    }


@pytest.fixture
def event(event_data):
    return Event.objects.create(**event_data)
