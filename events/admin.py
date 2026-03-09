from django.contrib import admin

from events.models import (
    Event,
    EventAttachment,
    EventCategory,
    Notification,
    RSVP,
    Waitlist,
)


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "color"]
    search_fields = ["name"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "event_date", "location", "created_at"]
    list_filter = ["event_date", "category", "created_at"]
    search_fields = ["title", "description", "location"]
    raw_id_fields = ["creator"]
    date_hierarchy = "event_date"


@admin.register(EventAttachment)
class EventAttachmentAdmin(admin.ModelAdmin):
    list_display = ["filename", "event", "uploaded_at"]
    raw_id_fields = ["event"]


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "status", "created_at"]
    list_filter = ["status", "created_at"]
    raw_id_fields = ["event", "user"]


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "position", "joined_at"]
    raw_id_fields = ["event", "user"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "notification_type",
        "is_read",
        "created_at",
        "related_event",
    ]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["user__email", "message", "related_event__title"]
    raw_id_fields = ["user", "related_event", "actor"]
