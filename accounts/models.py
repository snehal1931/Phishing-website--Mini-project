from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.png'

    def total_scans(self):
        return self.user.scanhistory_set.count()

    def phishing_found(self):
        return self.user.scanhistory_set.filter(result='Phishing').count()
