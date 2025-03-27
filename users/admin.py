from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClientProfile, LawyerProfile, Consultation, Review, Notification

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


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('client', 'lawyer', 'date', 'time', 'status', 'mode', 'created_at')
    list_filter = ('status', 'mode', 'date')
    search_fields = ('client__user__username', 'lawyer__user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'lawyer', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('client__user__username', 'lawyer__user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')