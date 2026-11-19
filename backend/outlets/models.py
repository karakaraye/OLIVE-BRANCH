from django.db import models


class Outlet(models.Model):
    name = models.CharField(max_length=80, unique=True)
