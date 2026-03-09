from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.core.files.storage import default_storage
from events.models import Event, EventCategory, RSVP, EventAttachment
from django.views.decorators.http import require_http_methods

from events.forms import EventForm, AttachmentValidationMixin
from events.notifications import notify_event_created, notify_event_updated, notify_rsvp
from events.rate_limit import is_rate_limited
from events.services import handle_rsvp


def health(request):
    """Lightweight liveness probe — no DB hit, no auth."""
    return HttpResponse("ok")


def _identity(request):
    if request.user.is_authenticated:
        return f"u:{request.user.pk}"
    return f"ip:{request.META.get('REMOTE_ADDR', 'unknown')}"


def _get_event_by_slug_or_legacy_id(slug):
    if isinstance(slug, str) and slug.isdigit():
        return get_object_or_404(Event, pk=int(slug))
    return get_object_or_404(Event, slug=slug)


def home(request):
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    upcoming_events = Event.objects.filter(
        event_date__gte=today
    ).select_related("category").order_by("event_date", "event_time")[:6]
    return render(
        request,
        "events/home.html",
        {
            "upcoming_events": upcoming_events,
            "today": today,
            "tomorrow": tomorrow,
        },
    )


def event_list(request):
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    category = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    date_from_raw = request.GET.get("date_from", "").strip()
    date_to_raw = request.GET.get("date_to", "").strip()

    events = Event.objects.filter(event_date__gte=today).select_related("category")
    if category:
        events = events.filter(category__name=category)
    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )
    if date_from_raw:
        try:
            import datetime
            date_from = datetime.date.fromisoformat(date_from_raw)
            events = events.filter(event_date__gte=date_from)
        except ValueError:
            pass
    if date_to_raw:
        try:
            import datetime
            date_to = datetime.date.fromisoformat(date_to_raw)
            events = events.filter(event_date__lte=date_to)
        except ValueError:
            pass

    events = events.order_by("event_date", "event_time")
    categories = EventCategory.objects.all()
    return render(
        request,
        "events/event_list.html",
        {
            "events": events,
            "categories": categories,
            "selected_category": category,
            "search_query": query,
            "date_from": date_from_raw,
            "date_to": date_to_raw,
            "today": today,
            "tomorrow": tomorrow,
        },
    )


@login_required
def event_create(request):
    if is_rate_limited(
        "event_create",
        _identity(request),
        settings.EVENT_CREATE_RATE_LIMIT_COUNT,
        settings.EVENT_CREATE_RATE_LIMIT_WINDOW,
    ):
        return HttpResponse("Rate limit exceeded for creating events", status=429)

    if request.method == "POST":
        form = EventForm(request.POST)
        attachments = request.FILES.getlist("attachments")
        image = request.FILES.get("image")

        attachment_error = AttachmentValidationMixin.validate(attachments)
        if attachment_error:
            messages.error(request, attachment_error)
            categories = EventCategory.objects.all()
            return render(request, "events/event_create.html", {"categories": categories, "form": form})

        if form.is_valid():
            cd = form.cleaned_data
            category_id = cd.get("category")
            category = EventCategory.objects.get(id=category_id) if category_id else None

            event = Event.objects.create(
                creator=request.user,
                title=cd["title"],
                description=cd["description"],
                event_date=cd["event_date"],
                event_time=cd.get("event_time"),
                location=cd["location"],
                location_url=cd["location_url"],
                category=category,
                image=image,
                max_attendees=cd.get("max_attendees"),
                is_public_attendees=cd.get("is_public_attendees", True),
                whatsapp_group_link=cd["whatsapp_group_link"],
            )

            for uploaded in attachments:
                EventAttachment.objects.create(
                    event=event,
                    file=uploaded,
                    filename=uploaded.name,
                )

            notify_event_created(event, request.user)
            messages.success(request, "Event created successfully!")
            return redirect("events:event_detail", slug=event.slug)
        else:
            messages.error(request, "Please correct the errors below.")
            categories = EventCategory.objects.all()
            return render(request, "events/event_create.html", {"categories": categories, "form": form})

    form = EventForm()
    categories = EventCategory.objects.all()
    return render(request, "events/event_create.html", {"categories": categories, "form": form})


def event_detail(request, slug):
    event = _get_event_by_slug_or_legacy_id(slug)
    user_rsvp = None
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(event=event, user=request.user).first()

    attendees = event.rsvps.filter(status="going") if event.is_public_attendees else []

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "user_rsvp": user_rsvp,
            "attendees": attendees,
        },
    )


@login_required
def event_edit(request, slug):
    event = _get_event_by_slug_or_legacy_id(slug)
    if event.creator != request.user:
        messages.error(request, "You can only edit your own events.")
        return redirect("events:event_detail", slug=event.slug)

    if request.method == "POST":
        form = EventForm(request.POST)
        attachments = request.FILES.getlist("attachments")
        image = request.FILES.get("image")

        requested_gallery_link = request.POST.get("gallery_link", "")
        if requested_gallery_link and not event.can_edit_gallery():
            messages.error(
                request, "Gallery link can only be set after the event date."
            )
            return redirect("events:event_edit", slug=event.slug)

        attachment_error = AttachmentValidationMixin.validate(attachments, event=event)
        if attachment_error:
            messages.error(request, attachment_error)
            categories = EventCategory.objects.all()
            return render(
                request,
                "events/event_edit.html",
                {"event": event, "categories": categories, "form": form},
            )

        if form.is_valid():
            cd = form.cleaned_data
            category_id = cd.get("category")
            event.title = cd["title"]
            event.description = cd["description"]
            event.event_date = cd["event_date"]
            event.event_time = cd.get("event_time")
            event.location = cd["location"]
            event.location_url = cd["location_url"]
            event.category = EventCategory.objects.get(id=category_id) if category_id else None
            event.whatsapp_group_link = cd["whatsapp_group_link"]
            if image:
                event.image = image
            if event.can_edit_gallery():
                event.gallery_link = cd["gallery_link"]

            max_attendees = cd.get("max_attendees")
            event.max_attendees = max_attendees
            event.is_public_attendees = cd.get("is_public_attendees", True)

            event.save()

            for uploaded in attachments:
                EventAttachment.objects.create(
                    event=event,
                    file=uploaded,
                    filename=uploaded.name,
                )

            notify_event_updated(event, request.user)
            messages.success(request, "Event updated!")
            return redirect("events:event_detail", slug=event.slug)
        else:
            messages.error(request, "Please correct the errors below.")
            categories = EventCategory.objects.all()
            return render(
                request,
                "events/event_edit.html",
                {"event": event, "categories": categories, "form": form},
            )

    form = EventForm(initial={
        "title": event.title,
        "description": event.description,
        "event_date": event.event_date,
        "event_time": event.event_time,
        "location": event.location,
        "location_url": event.location_url,
        "category": event.category_id,
        "max_attendees": event.max_attendees,
        "is_public_attendees": event.is_public_attendees,
        "whatsapp_group_link": event.whatsapp_group_link,
        "gallery_link": event.gallery_link,
    })
    categories = EventCategory.objects.all()
    return render(
        request, "events/event_edit.html", {"event": event, "categories": categories, "form": form}
    )


@login_required
@require_http_methods(["POST"])
def rsvp(request, slug):
    if is_rate_limited(
        "rsvp",
        _identity(request),
        settings.RSVP_RATE_LIMIT_COUNT,
        settings.RSVP_RATE_LIMIT_WINDOW,
    ):
        return HttpResponse("Rate limit exceeded for RSVP", status=429)

    event = _get_event_by_slug_or_legacy_id(slug)
    status = request.POST.get("status")

    if status not in ["going", "maybe", "not_going"]:
        messages.error(request, "Invalid RSVP status.")
        return redirect("events:event_detail", slug=event.slug)

    outcome = handle_rsvp(event, request.user, status)
    notify_rsvp(event, request.user, status)

    if outcome == "waitlisted":
        messages.info(request, "Event is full. You were added to the waitlist.")
    else:
        messages.success(request, f"RSVP updated to {status}!")
    return redirect("events:event_detail", slug=event.slug)


@login_required
@require_http_methods(["POST"])
def event_delete(request, slug):
    event = _get_event_by_slug_or_legacy_id(slug)
    if event.creator != request.user:
        messages.error(request, "You can only delete your own events.")
        return redirect("events:event_detail", slug=event.slug)
    event.is_deleted = True
    event.save(update_fields=["is_deleted"])
    messages.success(request, f'"{event.title}" has been deleted.')
    return redirect("users:dashboard")


@login_required
@require_http_methods(["POST"])
def attachment_delete(request, pk):
    attachment = get_object_or_404(EventAttachment, pk=pk)
    if attachment.event.creator != request.user:
        return HttpResponse("Forbidden", status=403)
    # Delete the file from storage, then the DB record
    if attachment.file:
        default_storage.delete(attachment.file.name)
    attachment.delete()
    return HttpResponse("", status=200)


def past_events(request):
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    events = Event.objects.filter(event_date__lt=today).select_related("category").order_by(
        "-event_date", "-event_time"
    )
    return render(
        request,
        "events/past_events.html",
        {
            "events": events,
            "today": today,
            "tomorrow": tomorrow,
        },
    )


def event_ics(request, slug):
    event = _get_event_by_slug_or_legacy_id(slug)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//ADA Events//EN
BEGIN:VEVENT
UID:{event.pk}@ada-events
DTSTAMP:{timezone.now().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{event.event_date.strftime("%Y%m%d")}{f"T{event.event_time.strftime('%H%M%S')}" if event.event_time else ""}
SUMMARY:{event.title}
DESCRIPTION:{event.description}
LOCATION:{event.location}
END:VEVENT
END:VCALENDAR"""

    response = HttpResponse(ics_content, content_type="text/calendar")
    response["Content-Disposition"] = f"attachment; filename=event_{event.slug}.ics"
    return response
