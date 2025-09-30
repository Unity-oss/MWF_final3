# home/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Sale, Stock, Notification

@receiver(post_save, sender=Sale)
def create_sale_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,   # or assign to a manager/admin
            message=f"New sale: {instance.product} - ${instance.amount}",
            activity_type="success"
        )

@receiver(post_save, sender=Stock)
def create_stock_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,   # or whoever is responsible
            message=f"New stock added: {instance.product} (Qty: {instance.quantity})",
            activity_type="info"
        )
