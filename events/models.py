from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import URLValidator

from events.managers import EventManager
from events.utils import attachment_upload_to


class EventCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, default="calendar", help_text="Lucide icon name (https://lucide.dev)")
    color = models.CharField(max_length=7, default="#6366f1")

    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=240, blank=True, db_index=True)
    description = models.TextField()
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    location_url = models.URLField(
        blank=True, default="", validators=[URLValidator(schemes=["http", "https"])]
    )
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_public_attendees = models.BooleanField(default=True)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    whatsapp_group_link = models.URLField(
        blank=True,
        default="",
        validators=[URLValidator(schemes=["http", "https", "wa"])],
    )
    gallery_link = models.URLField(
        blank=True, default="", validators=[URLValidator(schemes=["http", "https"])]
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EventManager()

    class Meta:
        ordering = ["event_date", "event_time"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:220] or "event"
            slug = base_slug
            counter = 2
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix = f"-{counter}"
                slug = f"{base_slug[: 240 - len(suffix)]}{suffix}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        if self.event_date > timezone.now().date():
            return True
        if self.event_date == timezone.now().date() and self.event_time:
            return self.event_time > timezone.now().time()
        return False

    @property
    def is_past(self):
        return not self.is_upcoming

    @property
    def attendee_count(self):
        return self.rsvps.filter(status="going").count()

    @property
    def is_full(self):
        if self.max_attendees is None:
            return False
        return self.attendee_count >= self.max_attendees

    def can_edit_gallery(self):
        return self.is_past


class EventAttachment(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to=attachment_upload_to)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class RSVP(models.Model):
    STATUS_CHOICES = [
        ("going", "Going"),
        ("maybe", "Maybe"),
        ("not_going", "Can't Go"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rsvps"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="going")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["event", "user"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.event} ({self.status})"


class Waitlist(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="waitlist")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="waitlist"
    )
    position = models.PositiveIntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["event", "user"]
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "position"], name="uniq_waitlist_event_position"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.event} (position {self.position})"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("event_created", "New Event"),
        ("event_updated", "Event Updated"),
        ("rsvp", "New RSVP"),
        ("reminder", "Event Reminder"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    related_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="triggered_notifications",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, default="")
    dedupe_key = models.CharField(max_length=120, blank=True, default="", db_index=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["notification_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.user}"
