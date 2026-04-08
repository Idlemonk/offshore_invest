from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

class UserMetadata(models.Model):
    """User preferences and metadata"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metadata')
    
    # Preferences
    dark_mode = models.BooleanField(default=True)
    preferred_currency = models.CharField(
        max_length=3,
        choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')],
        default='USD'
    )
    language = models.CharField(max_length=10, default='en')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=200, blank=True)

    # Activity tracking (for inactive account detection)
    last_activity = models.DateTimeField(auto_now = True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_user_metadata'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"

# Signal to create metadata when user is created
@receiver(post_save, sender=User)
def create_user_metadata(sender, instance, created, **kwargs):
    """Create metadata automatically when a new user is created"""
    if created:
        UserMetadata.objects.create(user=instance)


