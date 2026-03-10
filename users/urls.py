from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notifications_inbox, name="notifications_inbox"),
    path(
        "notifications/<int:pk>/read/",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path(
        "notifications/read-all/",
        views.notifications_mark_all_read,
        name="notifications_mark_all_read",
    ),
    path(
        "notifications/<int:pk>/open/",
        views.notification_open,
        name="notification_open",
    ),
]
