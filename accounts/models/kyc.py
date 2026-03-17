from django.db import models
from .user import User


class KYC(models.Model):

        user = models.OneToOneField(User, on_delete=models.CASCADE)