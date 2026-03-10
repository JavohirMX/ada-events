from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.contrib import messages

from events.models import RSVP
from events.models import Notification
from users.models import User
from users.forms import ProfileEditForm


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "users/profile.html", {"profile_user": user})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("users:dashboard")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def dashboard(request):
    today = timezone.now().date()
    my_upcoming_events = request.user.created_events.filter(
        event_date__gte=today
    ).order_by("event_date", "event_time")
    attending_rsvps = (
        RSVP.objects.filter(user=request.user, event__event_date__gte=today)
        .select_related("event")
        .order_by("event__event_date", "event__event_time")
    )
    my_past_events = request.user.created_events.filter(
        event_date__lt=today
    ).order_by("-event_date")[:10]
    past_rsvps = (
        RSVP.objects.filter(user=request.user, event__event_date__lt=today)
        .select_related("event")
        .order_by("-event__event_date")[:10]
    )
    return render(
        request,
        "users/dashboard.html",
        {
            "my_upcoming_events": my_upcoming_events,
            "attending_rsvps": attending_rsvps,
            "my_past_events": my_past_events,
            "past_rsvps": past_rsvps,
        },
    )


@login_required
def notifications_inbox(request):
    notifications = request.user.notifications.order_by("-created_at")
    return render(
        request,
        "users/notifications_inbox.html",
        {"notifications": notifications},
    )


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if notification.user != request.user:
        return HttpResponseForbidden(b"Not allowed")
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("users:notifications_inbox")


@login_required
@require_POST
def notifications_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect("users:notifications_inbox")


@login_required
def notification_open(request, pk):
    """Mark a notification as read and redirect to its link."""
    notification = get_object_or_404(Notification, pk=pk)
    if notification.user != request.user:
        return HttpResponseForbidden(b"Not allowed")
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    if notification.link:
        return redirect(notification.link)
    return redirect("users:notifications_inbox")
