from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

import misaka

from groups.models import Group

User = settings.AUTH_USER_MODEL

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, related_name = 'posts', on_delete = models.CASCADE)
    created_date = models.DateTimeField(auto_now = True)
    message = models.TextField()
    message_html = models.TextField(editable = False)
    group = models.ForeignKey(Group, related_name = 'posts', on_delete = models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:single', kwargs = {'pk': self.pk, 'email': self.user.email})
    
    class Meta:
        ordering = ['-created_date']
        unique_together = ['user', 'message']

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name = 'comments', on_delete = models.CASCADE)
    author = models.CharField(max_length = 256)
    text = models.TextField()
    created_at = models.DateTimeField(default = timezone.now)
    approved_comment = models.BooleanField(default = False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text