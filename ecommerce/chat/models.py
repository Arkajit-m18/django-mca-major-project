from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from rooms.models import Room 

User = settings.AUTH_USER_MODEL

# Create your models here.

class Message(models.Model):
    author = models.ForeignKey(User, related_name = 'author_messages', on_delete = models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    room = models.ForeignKey(Room, default = '', related_name = 'author_messages', on_delete = models.CASCADE)

    def last_10_messages(room_name):
        return Message.objects.filter(room__name = room_name).order_by('-timestamp').all()[:10][::-1]

    def active_users(room_name):
        userlist = []
        room = Room.objects.filter(name = room_name)[0]
        for member in room.members.all():
            userlist.append(member.email)
        return userlist

    def __str__(self):
        return self.author.email