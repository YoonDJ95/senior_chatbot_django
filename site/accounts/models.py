from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # 전화번호 필드
    address = models.CharField(max_length=255, blank=True, null=True)
    detailed_address = models.CharField(max_length=255, blank=True, null=True)
    business_types = models.JSONField(default=list, blank=True)  # 업종을 리스트 형식으로 저장

    def __str__(self):
        return f"Profile of {self.user.username}"
