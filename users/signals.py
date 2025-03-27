from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ClientProfile, LawyerProfile
from django.core.mail import send_mail
from .models import Consultation

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_client:
            ClientProfile.objects.create(user=instance)
        elif instance.is_lawyer:
            LawyerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.is_client and hasattr(instance, 'clientprofile'):
        instance.clientprofile.save()
    elif instance.is_lawyer and hasattr(instance, 'lawyerprofile'):
        instance.lawyerprofile.save()
