from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User


# Tự tạo UserOnlineStatus khi có User mới được tạo
@receiver(post_save, sender=User)
def create_online_status(sender, instance, created, **kwargs):
    if created:
        from home.models import UserOnlineStatus
        UserOnlineStatus.objects.get_or_create(user=instance)


# Khi đăng nhập → is_online = True
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    from home.models import UserOnlineStatus
    status, _ = UserOnlineStatus.objects.get_or_create(user=user)
    status.is_online = True
    status.last_seen = timezone.now()
    status.save()


# Khi đăng xuất → is_online = False, lưu last_seen
@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    if user is None:
        return
    from home.models import UserOnlineStatus
    status, _ = UserOnlineStatus.objects.get_or_create(user=user)
    status.is_online = False
    status.last_seen = timezone.now()
    status.save()
