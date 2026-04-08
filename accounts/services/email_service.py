"""
Email services for sending notifications
"""
from django.conf import settings #This imports your settings
def send_kyc_reminder_email(user):
        """
        Send KYC reminder after deposit
        """

        subject = "Complete KYC to have unlimited access"
        html_message = 'render_to_string'('accounts/email/kc_reminder.html', {
                'user': user,
                'site_url' : settings.SITE_URL,
        })
        plain_message = f"""
Hello {user.username},

Thank you for depositing funds with Offshore Investment!

To have unlimited access to your funds and start investing, please complete your KYC verification.

Click here to verify: {settings.SITE_URL}/accounts/kyc/wizard/

If you don't complete KYC, you won't be able to withdraw or invest.

Thank you,
Offshore Investment Team
"""
        send_mail(
                subject=subject,
                message=plain_message,
                form_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
        )

def send_inactive_account_email(user):
        """
        Send email to inactive account
        """

        subject = "Your account has been flagged as inactive"
        html_message = render_to_string('accounts/emails/inactive_account.html',{
                'user': user,
                'site_url' : settings.SITE_URL,
        })
        send_mail(
                subject=subject,
                message=f"Hello {user.username}, \n\nYour account has been flagged as inactive. Login to reactivate. \n\n{settings.SITE_URL}/accounts/login/",
                from_email = settings.DEFAULT_FROM_EMAIL,
                recipient_list = [user.email],
                html_message = html_message,
                fail_silently = False,
        )