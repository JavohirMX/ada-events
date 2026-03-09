from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    bio = models.TextField(blank=True, default="")
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    whatsapp_link = models.URLField(blank=True, default="")
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email or self.username

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"username": self.username})
