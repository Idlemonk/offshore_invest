from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import (
    homepage, signup, login_view, logout_view,
    kyc_wizard, kyc_status, kyc_retry
)
#from accounts import admin_tools

app_name = 'accounts'

urlpatterns = [
    # Homepage
    path('', homepage, name='homepage'),
    # KYC URLS
    path('kyc/wizard/', kyc_wizard, name='kyc_wizard'),
    path('kyc/status/', kyc_status, name = 'kyc_status'),
    path('kyc/retry/',  kyc_retry, name='kyc_retry'),
    
    # Authentication
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    #Admin KYC URLs (superuser only)
    #path('admin/kyc/dashboard/', admin_tools.kyc_dashboard, name='kyc_dashboard'),
    #path('admin/kyc/review/<int:kyc_id>/', admin_tools.kyc_review, name = "kyc_review"),
    
    # Password Reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
         ]

    

    

