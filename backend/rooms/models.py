from django.db import models


class RoomType(models.Model):
    name = models.CharField(max_length=80, unique=True)


class Room(models.Model):
    number = models.CharField(max_length=16, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
