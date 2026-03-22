from django.db import models

class UserProfileManager(models.Manager):
    """Custom manager for UserProfile model"""
    
    def get_verified_users(self):
        """Return only users with verified KYC"""
        return self.filter(kyc_status='VERIFIED')
    
    def get_pending_kyc(self):
        """Return users pending KYC verification"""
        return self.filter(kyc_status='PENDING')
    
    def get_recent_users(self, days=30):
        """Return users who joined in last X days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)