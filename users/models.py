from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now




class User(AbstractUser):
    email = models.EmailField(unique=True)  
    is_client = models.BooleanField(default=False)
    is_lawyer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.username

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100,  default="Unknown")

    def __str__(self):
        return self.user.username

class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name="lawyer_profile")
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)  
    verified = models.BooleanField(default=False)
    address = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    location = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100,  default="Unknown")

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"
   

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lawyer_bookings')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.client} with {self.lawyer} on {self.appointment_date}"


class Consultation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    MODE_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In-Person'),
        ('phone', 'Phone Call'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.PROTECT, related_name='consultations')
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.PROTECT, related_name='consultations')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='online')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track updates

    def __str__(self):
        return f"{self.client.user.username} with {self.lawyer.user.username} on {self.date} at {self.time} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']  # Show newest consultations first

    def save(self, *args, **kwargs):
        """Prevent scheduling past consultations."""
        if self.date < now().date():
            raise ValueError("Consultation date cannot be in the past.")
        super().save(*args, **kwargs)

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:30]}"
