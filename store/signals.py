from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import User_Activity

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    User_Activity.objects.filter(user=user, logout_time__isnull=True).update(logout_time=now())  # Close previous session
    User_Activity.objects.create(user=user)  # Start a new session

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        activity = User_Activity.objects.filter(user=user, logout_time__isnull=True).last()
        if activity:
            activity.logout_time = now()
            activity.save()