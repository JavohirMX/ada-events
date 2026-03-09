from django.db import models


class EventQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)


class EventManager(models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return EventQuerySet(self.model, using=self._db)
