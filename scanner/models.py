from django.db import models
from django.contrib.auth.models import User
import json


class ScanHistory(models.Model):
    RESULT_CHOICES = [
        ('Safe', 'Safe'),
        ('Phishing', 'Phishing'),
    ]

    CATEGORY_CHOICES = [
        ('Link', 'Link (General)'),
        ('Email', 'Email Content'),
        ('Message', 'SMS/WhatsApp Message'),
        ('Other', 'Other/Unknown'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Link')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    confidence = models.FloatField(default=0.0)   # 0-100 %
    features_json = models.TextField(blank=True, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.user.username} | {self.result} | {self.url[:60]}"

    def get_features(self):
        try:
            return json.loads(self.features_json)
        except Exception:
            return {}

    @property
    def is_phishing(self):
        return self.result == 'Phishing'

    @property
    def confidence_int(self):
        return int(self.confidence)
