from django.urls import path
from events import views

app_name = "events"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("", views.home, name="home"),
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("events/<slug:slug>/edit/", views.event_edit, name="event_edit"),
    path("events/<slug:slug>/delete/", views.event_delete, name="event_delete"),
    path("events/<slug:slug>/rsvp/", views.rsvp, name="rsvp"),
    path("events/<slug:slug>/calendar.ics/", views.event_ics, name="event_ics"),
    path("attachments/<int:pk>/delete/", views.attachment_delete, name="attachment_delete"),
    path("past/", views.past_events, name="past_events"),
]
