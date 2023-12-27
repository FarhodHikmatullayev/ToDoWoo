from datetime import datetime, timedelta
from random import randint

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

NEW, CODE, REGISTERED = 'new', 'code', 'registered'


class User(AbstractUser):
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE, CODE),
        (REGISTERED, REGISTERED),
    )
    email = models.EmailField(null=True, blank=True, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    photo = models.ImageField(upload_to='users/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'heif', 'heic'])])
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)

    @staticmethod
    def create_code():
        code = "".join([str(randint(1, 10) % 10) for i in range(5)])
        return code

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Confirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmations')
    phone = models.CharField(max_length=13)
    code = models.CharField(max_length=5)
    time_limit = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        code = "".join([str(randint(1, 10) % 10) for i in range(5)])
        self.code = code
        self.time_limit = datetime.now() + timedelta(minutes=5)
        super(Confirmation, self).save(*args, **kwargs)
