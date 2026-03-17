from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
        first_name = models.CharField(max_length=120)
        last_name = models.CharField(max_length=120)
        email = models.EmailField(unique=True)

        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)

        created_at = models.DateTimeField(auto_now_add=True)
        
        objects = UserManager()

        USERNAME_FIELD = "email"
        REQUIRED_FIELDS = ["first_name", "last_name"]

        def __str__(self):
                return self.email
