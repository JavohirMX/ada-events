from django.db import transaction

from events.models import RSVP, Waitlist


@transaction.atomic
def add_user_to_waitlist(event, user):
    existing = (
        Waitlist.objects.select_for_update().filter(event=event, user=user).first()
    )
    if existing:
        return existing

    last = (
        Waitlist.objects.select_for_update()
        .filter(event=event)
        .order_by("-position")
        .first()
    )
    next_position = 1 if not last else last.position + 1
    return Waitlist.objects.create(event=event, user=user, position=next_position)


@transaction.atomic
def promote_next_waitlisted_user(event):
    if event.max_attendees is None or event.attendee_count >= event.max_attendees:
        return None

    entry = (
        Waitlist.objects.select_for_update()
        .filter(event=event)
        .order_by("position", "joined_at")
        .first()
    )
    if not entry:
        return None

    rsvp, _ = RSVP.objects.update_or_create(
        event=event,
        user=entry.user,
        defaults={"status": "going"},
    )
    entry.delete()

    for idx, row in enumerate(
        Waitlist.objects.filter(event=event).order_by("position", "joined_at"), start=1
    ):
        if row.position != idx:
            row.position = idx
            row.save(update_fields=["position"])

    return rsvp


@transaction.atomic
def handle_rsvp(event, user, desired_status):
    existing = RSVP.objects.filter(event=event, user=user).first()
    previous_status = existing.status if existing else None

    if desired_status != "going":
        RSVP.objects.update_or_create(
            event=event,
            user=user,
            defaults={"status": desired_status},
        )
        Waitlist.objects.filter(event=event, user=user).delete()

        if previous_status == "going":
            promote_next_waitlisted_user(event)
        return "updated_non_going"

    if previous_status == "going":
        Waitlist.objects.filter(event=event, user=user).delete()
        return "going"

    if event.max_attendees is None or event.attendee_count < event.max_attendees:
        RSVP.objects.update_or_create(
            event=event,
            user=user,
            defaults={"status": "going"},
        )
        Waitlist.objects.filter(event=event, user=user).delete()
        return "going"

    add_user_to_waitlist(event, user)
    return "waitlisted"
