import pytest
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_renders_for_logged_in_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse("users:dashboard"))
        assert response.status_code == 200

    def test_dashboard_shows_upcoming_events_created_by_user(self, client, user):
        from events.models import Event

        Event.objects.create(
            creator=user,
            title="Upcoming Run",
            description="Morning run",
            event_date=timezone.now().date() + timedelta(days=1),
            location="Bali",
        )
        Event.objects.create(
            creator=user,
            title="Past Run",
            description="Old run",
            event_date=timezone.now().date() - timedelta(days=1),
            location="Bali",
        )

        client.force_login(user)
        response = client.get(reverse("users:dashboard"))

        content = response.content.decode()
        assert "Upcoming Run" in content
        # Past events are now rendered in the collapsible "Past Events (Created)" section
        assert "Past Run" in content

    def test_dashboard_includes_mobile_shell_marker(self, client, user):
        client.force_login(user)
        response = client.get(reverse("users:dashboard"))
        assert response.status_code == 200
        assert 'data-mobile-dashboard-shell="true"' in response.content.decode()


@pytest.mark.django_db
class TestAuthMobileTemplates:
    def test_login_template_includes_mobile_auth_marker(self, client):
        response = client.get(reverse("account_login"))
        assert response.status_code == 200
        assert 'data-mobile-auth-form="true"' in response.content.decode()

    def test_signup_template_includes_mobile_auth_marker(self, client):
        response = client.get(reverse("account_signup"))
        assert response.status_code == 200
        assert 'data-mobile-auth-form="true"' in response.content.decode()


@pytest.mark.django_db
class TestNavbarMobileUX:
    def test_home_includes_mobile_brand_marker(self, client):
        response = client.get(reverse("home"))
        assert response.status_code == 200
        assert 'data-mobile-brand="Events"' in response.content.decode()

    def test_authenticated_nav_includes_avatar_only_trigger_and_notification_icon(
        self, client, user
    ):
        client.force_login(user)
        response = client.get(reverse("home"))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-user-trigger="avatar-only"' in content
        assert 'data-navbar-notifications-button="true"' in content
        assert 'data-notifications-icon="true"' in content

    def test_guest_nav_auth_actions_are_no_wrap(self, client):
        response = client.get(reverse("home"))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-auth-links-nowrap="true"' in content


@pytest.mark.django_db
class TestNotificationsViews:
    def test_notifications_inbox_requires_login(self, client):
        response = client.get(reverse("users:notifications_inbox"))
        assert response.status_code in (302, 301)

    def test_notifications_inbox_renders_for_user(self, client, user):
        from events.models import Notification

        Notification.objects.create(
            user=user,
            notification_type="event_created",
            message="New event",
        )
        client.force_login(user)
        response = client.get(reverse("users:notifications_inbox"))
        assert response.status_code == 200
        assert "New event" in response.content.decode()

    def test_mark_notification_read(self, client, user):
        from events.models import Notification

        notification = Notification.objects.create(
            user=user,
            notification_type="event_created",
            message="Unread",
            is_read=False,
        )
        client.force_login(user)
        response = client.post(
            reverse("users:notification_mark_read", args=[notification.pk])
        )
        assert response.status_code == 302
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_notifications_read(self, client, user):
        from events.models import Notification

        Notification.objects.create(
            user=user,
            notification_type="event_created",
            message="n1",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            notification_type="event_updated",
            message="n2",
            is_read=False,
        )
        client.force_login(user)
        response = client.post(reverse("users:notifications_mark_all_read"))
        assert response.status_code == 302
        assert Notification.objects.filter(user=user, is_read=False).count() == 0


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_requires_login(self, client, user):
        response = client.get(reverse("users:profile", args=[user.username]))
        assert response.status_code in (302, 301)

    def test_profile_renders_for_authenticated_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse("users:profile", args=[user.username]))
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_profile_email_is_visible_to_profile_owner_only(self, client):
        from users.models import User

        owner = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="pass12345",
        )
        viewer = User.objects.create_user(
            username="viewer1",
            email="viewer1@example.com",
            password="pass12345",
        )

        client.force_login(owner)
        own_profile = client.get(reverse("users:profile", args=[owner.username]))
        assert owner.email in own_profile.content.decode()

        client.force_login(viewer)
        other_profile = client.get(reverse("users:profile", args=[owner.username]))
        other_profile_content = other_profile.content.decode()
        assert owner.username in other_profile_content
        assert owner.email not in other_profile_content

    def test_profile_edit_requires_login(self, client):
        response = client.get(reverse("users:profile_edit"))
        assert response.status_code in (302, 301)

    def test_profile_edit_renders_for_logged_in_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse("users:profile_edit"))
        assert response.status_code == 200

    def test_profile_edit_updates_username_bio_and_whatsapp(self, client, user):
        client.force_login(user)
        payload = {
            "username": "updateduser",
            "bio": "Updated bio",
            "whatsapp_link": "https://wa.me/628123456789",
        }
        response = client.post(reverse("users:profile_edit"), data=payload)

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.username == "updateduser"
        assert user.bio == "Updated bio"
        assert user.whatsapp_link == "https://wa.me/628123456789"

    def test_profile_edit_updates_profile_photo(self, client, user):
        client.force_login(user)
        photo = SimpleUploadedFile(
            name="avatar.gif",
            content=(
                b"GIF87a\x01\x00\x01\x00\x80\x00\x00"
                b"\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
                b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )
        payload = {
            "username": user.username,
            "bio": user.bio,
            "whatsapp_link": user.whatsapp_link,
            "profile_photo": photo,
        }

        response = client.post(reverse("users:profile_edit"), data=payload)

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.profile_photo
        assert user.profile_photo.name.startswith("profiles/")

    def test_profile_edit_rejects_duplicate_username(self, client, user):
        from users.models import User

        User.objects.create_user(
            username="existingname",
            email="existing@example.com",
            password="pass12345",
        )

        client.force_login(user)
        response = client.post(
            reverse("users:profile_edit"),
            data={
                "username": "existingname",
                "bio": "Bio",
                "whatsapp_link": "https://wa.me/628123456789",
            },
        )

        assert response.status_code == 200
        assert "already" in response.content.decode().lower()
        user.refresh_from_db()
        assert user.username == "testuser"


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email(self, user_data):
        from users.models import User

        user = User.objects.create_user(**user_data)

        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.check_password(user_data["password"])
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_bio(self, user_data_with_bio):
        from users.models import User

        user = User.objects.create_user(**user_data_with_bio)

        assert user.bio == user_data_with_bio["bio"]

    def test_create_user_without_bio(self, user_data):
        from users.models import User

        user = User.objects.create_user(**user_data)

        assert user.bio is None or user.bio == ""

    def test_create_user_with_profile_photo(self, user_data_with_profile_photo):
        from users.models import User

        user = User.objects.create_user(**user_data_with_profile_photo)

        assert user.profile_photo is not None
        assert user.profile_photo.name.startswith("profiles/test_photo")

    def test_create_user_without_profile_photo(self, user_data):
        from users.models import User

        user = User.objects.create_user(**user_data)

        assert not user.profile_photo

    def test_create_user_with_whatsapp_link(self, user_data_with_whatsapp):
        from users.models import User

        user = User.objects.create_user(**user_data_with_whatsapp)

        assert user.whatsapp_link == user_data_with_whatsapp["whatsapp_link"]

    def test_create_user_without_whatsapp_link(self, user_data):
        from users.models import User

        user = User.objects.create_user(**user_data)

        assert user.whatsapp_link is None or user.whatsapp_link == ""

    def test_create_superuser(self, superuser_data):
        from users.models import User

        user = User.objects.create_superuser(**superuser_data)

        assert user.username == superuser_data["username"]
        assert user.email == superuser_data["email"]
        assert user.check_password(superuser_data["password"])
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_defaults(self, superuser_data):
        from users.models import User

        user = User.objects.create_superuser(**superuser_data)

        assert user

    def test_user_str_representation(self, user):
        assert str(user) == user.email

    def test_user_get_absolute_url(self, user):
        expected_url = reverse("users:profile", kwargs={"username": user.username})
        assert user.get_absolute_url() == expected_url

    def test_user_model_has_required_fields(self, user_data):
        from users.models import User
        from django.db import models

        user = User.objects.create_user(**user_data)

        assert hasattr(user, "username")
        assert hasattr(user, "email")
        assert hasattr(user, "password")
        assert hasattr(user, "bio")
        assert hasattr(user, "profile_photo")
        assert hasattr(user, "whatsapp_link")

    def test_user_email_is_unique(self, user_data):
        from users.models import User

        User.objects.create_user(**user_data)

        with pytest.raises(Exception):
            User.objects.create_user(
                username="differentuser",
                email=user_data["email"],
                password="password123",
            )

    def test_user_inherits_from_abstract_user(self, user_data):
        from users.models import User
        from django.contrib.auth.models import AbstractUser

        user = User.objects.create_user(**user_data)

        assert isinstance(user, AbstractUser)

    def test_profile_photo_upload_to(self, user_data_with_profile_photo):
        from users.models import User

        user = User.objects.create_user(**user_data_with_profile_photo)

        assert user.profile_photo.name.startswith("profiles/")
