"""
KYC (Know Your Customer) Models
Handles user identity verification, document Uploads, and verification tracking
"""

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class KYC(models.Model):
        """
        Main KYC verification record for a user
        """
        user = models.OneToOneField(User, on_delete=models.CASCADE)

#Status tracking
        status = models.CharField(
                max_length= 20,
                choices=[
                        ('NOT_STARTED', 'Not Started'),
                        ('PENDING', 'Pending Verification'),
                        ('VERIFIED', 'Verified'),
                        ('REJECTED', 'REJECTED'),
                        ('EXPIRED', 'Expired'),
                ],
                default = 'NOT_STARTED'
                )
#TimeStamps
        submitted_at = models.DateTimeField(null=True, blank=True)#When User first submitted 
        verified_at = models.DateTimeField(null=True, blank=True)#When admin aprroved
        expires_at = models.DateTimeField(null=True, blank=True)#@ years after verification

#Tracking
        review_started_at = models.DateTimeField(null=True, blank=True)# When admn started review 
        reviewed_by = models.ForeignKey(
                User,
                on_delete = models.SET_NULL,
                null = True,
                blank = True,
                related_name = 'reviewed_kyc'
        )
        #Notes (Internal Use Only)
        admin_notes = models.TextField(blank=True, help_text = "Internal notes for admin review")

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now = True)

        class Meta:
                db_table = 'account_kyc'
                verbose_name = 'KYC Verification'
                verbose_name_plural = 'KYC Verifications'
        def __str__(self):
                return f"{self.user.username} - {self.status}"
        
        def is_expired(self):
                """Check if verification has expired"""
                if self.expires_at and self.expires_at < timezone.now():
                        return True
                return False
        def calculate_expiry_date(self):
                """Calculate expiry date (2 years from verification)"""
                if self.verified_at:
                        return self.verified_at + timedelta(days=730) #2 years
                return None
        def mark_verified(self, admin_user):
                """Mark KYC as verified"""
                self.status = "VERIFIED"
                self.verified_at = timezone.now()
                self.expires_at = self.calculate_expiry_date()
                self.reviewed_by = admin_user
                self.save()

        def mark_rejected(self, admin_user):
                """Mark KYC as rejected """
                self.status = 'REJECTED'
                self.reviewed_by = admin_user
                self.save()

        def mark_expired(self):
                """Mark KYC as expired (Called by scheduled task)"""
                if self.is_expired():
                        self.status = 'EXPIRED'
                        self.save()

class KYCDocument(models.Model):
        """
        Individual documents uploaded for KYC verification
        """
        kyc = models.ForeignKey('KYC', on_delete=models.CASCADE, related_name='documents')

        #Document info
        document_type = models.CharField(
                max_length=20,
                choices=[
                        ('DIVERS_LICENSE', "Driver's_License"),
                        ('SELFIE', "Self with ID"),
                ]
        )

        # File Storage
        file = models.FileField(upload_to='kyc_documents/%y/%m/%d/')
        file_name = models.CharField(max_length=255)
        file_size = models.PositiveIntegerField(help_text="File size in bytes")

        #Status
        status = models.CharField(
                max_length=20,
                choices=[
                        ('PENDING', 'Pending Review'),
                        ('APPROVED', 'Approved'),
                        ('REJECTED', 'Rejected'),
                ],
                default='PENDING'
        )

        #Rejection tracking
        rejection_reason = models.CharField(
                max_length=50,
                choices=[
                        ('BLURRY', 'Image is blurry or unclear'),
                        ('WRONG_FORMAT', 'Wrong file format'),
                        ('FILE_TOO_LARGE', 'File size exceeds limit'),
                        ('EXPIRED', 'Document is expired'),
                        ('NAME_MISMATCH', 'Name does not match account'),
                        ('ADDRESS_MISMATCH', 'Address does not match'),
                        ('SELFIE_MISMATCH', 'Selfie does not match ID photo'),
                        ('INCOMPLETE', 'Incomplete document'),
                        ('OTHER', 'Other reason'),
                ],
                null = True,
                blank = True 
        )
        rejection_details = models.TextField(blank=True, help_text="Additional details about rejection")

        #TimeStamps
        uploaded_at = models.DateTimeField(auto_now_add = True)
        reviewed_at = models.DateTimeField(null=True, blank=True)

        class Meta:
                db_table = 'accounts_kyc_document'
                verbose_name = 'KYC Document'
                verbose_name_plural = 'KYC Documents'
                # Ensure one user can't upload multiple pending documents of same type
                unique_together = ['kyc', 'document_type', 'status']

        def __str__(self):
                return f"{self.kyc.user.username} - {self.document_type} - {self.status}"
        def approve(self):
                """ Approve this document """
                self.status = 'APPROVED'
                self.reviewed_at = timezone.now()
                self.save()

        def reject(self, reason, details=""):
                """Reject this document with reason"""
                self.status = 'REJECTED'
                self.rejection_reason = reason
                self.rejection_details = details
                self.reviewed_at = timezone.now()
                self.save()

class KYCFailedAttempt(models.Model):
        """
        Track failed KYC submission attempts
        """
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_failed_attempts')

        # Which document faies
        document_type = models.CharField(
                max_length = 20,
                choices = [
                        ('DIVERS_LICENSE', "Driver's License"),
                        ('SELFIE', 'Selfie with ID'),
                ]
        )

        # Why it failed
        failure_reason = models.CharField(max_length=50)
        failure_details = models.TextField(blank=True)

        # When it happened
        attempted_at = models.DateTimeField(auto_now_add = True)

        class Meta:
                db_table = 'accounts_kyc_failed_attempt'
                verbose_name = 'KYC Failed Attempt'
                verbose_name_plural = 'KYC Failed Attempts'
                ordering = ['-attempted_at']

        def __str__(self):
                return f"{self.user.username} - {self.document_type} - {self.attempted_at.strftime('%y-%m-%d')}"
        

