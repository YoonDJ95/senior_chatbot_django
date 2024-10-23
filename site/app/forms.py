from django import forms
from .models import Resume, Education, Experience, Certification

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'phone_number', 'address', 'detailed_address', 'self_introduction', 'birth_date']  # 'birth_date' 필드 추가
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'detailed_address': forms.TextInput(attrs={'class': 'form-control'}),
            'self_introduction': forms.Textarea(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})  # 생년월일 입력 필드
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'period', 'major', 'grade']  # 전공 필드 추가


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'period', 'position', 'role']

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'acquisition_date', 'issuing_agency']