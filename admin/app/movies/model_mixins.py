import uuid

from django.db import models


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CreatedModifiedMixin(CreatedMixin):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
