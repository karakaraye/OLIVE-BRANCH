from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    request_id = models.CharField(max_length=100, unique=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    occurred_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)
    affected_record = models.CharField(max_length=255)
