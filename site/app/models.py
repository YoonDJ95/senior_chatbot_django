from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.CharField(max_length=255)
    search_results = models.TextField(default="")  # 검색 결과를 텍스트로 저장
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.search_query}"

class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    detailed_address = models.CharField(max_length=255, blank=True, null=True)
    self_introduction = models.TextField(blank=True, null=True)  # 이 필드를 추가
    birth_date = models.DateField(null=True, blank=True)
    self_introduction = models.TextField(null=True, blank=True)
    preferred_industries = models.TextField(null=True, blank=True)  # 선호 업종을 저장할 필드

class Education(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)
    school = models.CharField(max_length=100)
    period = models.CharField(max_length=50)
    grade = models.CharField(max_length=10)
    major = models.CharField(max_length=100, null=True, blank=True)  # 전공 필드 추가

    def __str__(self):
        return self.school


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience_set')
    company = models.CharField(max_length=255, default='N/A')  # 여기를 company_name이 아니라 company로 설정
    period = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    role = models.CharField(max_length=255)


class Certification(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    acquisition_date = models.DateField(null=True, blank=True)  # 취득일자 필드 추가
    issuing_agency = models.CharField(max_length=100)  # 공증기관 필드 추가

    def __str__(self):
        return self.name
