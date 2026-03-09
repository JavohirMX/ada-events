import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def user_data_with_bio():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "bio": "This is a test bio",
    }


@pytest.fixture
def user_data_with_profile_photo():
    photo = SimpleUploadedFile(
        name="test_photo.jpg", content=b"fake image content", content_type="image/jpeg"
    )
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "profile_photo": photo,
    }


@pytest.fixture
def user_data_with_whatsapp():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "whatsapp_link": "https://wa.me/1234567890",
    }


@pytest.fixture
def superuser_data():
    return {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "adminpass123",
    }


@pytest.fixture
def user(db, user_data):
    from users.models import User

    return User.objects.create_user(**user_data)


@pytest.fixture
def user_with_bio(db, user_data_with_bio):
    from users.models import User

    return User.objects.create_user(**user_data_with_bio)


@pytest.fixture
def user_with_profile_photo(db, user_data_with_profile_photo):
    from users.models import User

    return User.objects.create_user(**user_data_with_profile_photo)


@pytest.fixture
def user_with_whatsapp(db, user_data_with_whatsapp):
    from users.models import User

    return User.objects.create_user(**user_data_with_whatsapp)


@pytest.fixture
def superuser(db, superuser_data):
    from users.models import User

    return User.objects.create_superuser(**superuser_data)
