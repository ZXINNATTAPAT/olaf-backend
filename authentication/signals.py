"""
Django signals for the authentication app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account


@receiver(post_save, sender=Account)
def account_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Account model post_save.
    """
    if created:
        # Handle new account creation
        pass
