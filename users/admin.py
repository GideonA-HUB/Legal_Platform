from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClientProfile, LawyerProfile

# Register the User model with Django's built-in UserAdmin
admin.site.register(User, UserAdmin)

# Register the ClientProfile model
@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username', 'address')

# Register the LawyerProfile model
@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'verified', 'address')
    list_filter = ('verified',)
    search_fields = ('user__username', 'specialization', 'license_number')
