from django.db import models
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length = 256, unique = True)
    description = models.TextField(blank = True, default = '')
    slug = models.SlugField(allow_unicode = True, unique = True)
    members = models.ManyToManyField(User, through = 'Membership')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.has_joined = True
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('rooms:single', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['name']

class Membership(models.Model):
    user = models.ForeignKey(User, related_name = 'user_rooms', on_delete = models.CASCADE)
    room = models.ForeignKey(Room, related_name = 'memberships', on_delete = models.CASCADE)

    def __str__(self):
        return self.user.email

    class Meta:
        unique_together = ['user', 'room']