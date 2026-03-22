from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from accounts.models.user import UserProfile
from accounts.models.metadata import UserMetadata

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserMetadataInline(admin.StackedInline):
    model = UserMetadata
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, UserMetadataInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_kyc_status')
    
    def get_kyc_status(self, instance):
        return instance.profile.kyc_status
    get_kyc_status.short_description = 'KYC Status'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
