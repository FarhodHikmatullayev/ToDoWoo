from django.db import models

from apps.users.models import User


class Task(models.Model):
    title = models.CharField(max_length=221)
    memo = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    important = models.BooleanField(default=False, null=True, blank=True)
    is_completed = models.BooleanField(default=False, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
