from django.urls import reverse

from events.models import Notification, RSVP


def _event_link(event):
    return reverse("events:event_detail", kwargs={"slug": event.slug})


def notify_event_created(event, actor):
    recipients = actor.__class__.objects.filter(is_active=True).exclude(pk=actor.pk)
    for user in recipients:
        Notification.objects.create(
            user=user,
            notification_type="event_created",
            message=f"New event: {event.title}",
            link=_event_link(event),
            related_event=event,
            actor=actor,
        )


def notify_event_updated(event, actor):
    attendees = (
        RSVP.objects.filter(event=event, status__in=["going", "maybe"])
        .exclude(user=actor)
        .select_related("user")
    )
    for rsvp in attendees:
        Notification.objects.create(
            user=rsvp.user,
            notification_type="event_updated",
            message=f"Event updated: {event.title}",
            link=_event_link(event),
            related_event=event,
            actor=actor,
        )


def notify_rsvp(event, actor, status):
    if actor == event.creator:
        return
    Notification.objects.create(
        user=event.creator,
        notification_type="rsvp",
        message=f"{actor.username} RSVP'd {status} to {event.title}",
        link=_event_link(event),
        related_event=event,
        actor=actor,
    )


def notify_event_reminder(event, users):
    for user in users:
        dedupe = f"reminder:{event.pk}:{user.pk}:{event.event_date.isoformat()}"
        if Notification.objects.filter(user=user, dedupe_key=dedupe).exists():
            continue
        Notification.objects.create(
            user=user,
            notification_type="reminder",
            message=f"Reminder: {event.title} is coming up soon",
            link=_event_link(event),
            related_event=event,
            dedupe_key=dedupe,
        )
