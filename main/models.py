from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.ForeignKey(User, models.CASCADE)

    def __str__(self):
        return self.user.username
