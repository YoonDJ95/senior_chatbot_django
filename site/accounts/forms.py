# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class SignupForm(forms.Form):
    email_id = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이메일 입력'}),
        label='E-mail'
    )
    email_domain = forms.ChoiceField(
        choices=[
            ('gmail.com', 'gmail.com'),
            ('naver.com', 'naver.com'),
            ('daum.net', 'daum.net'),
            ('hanmail.net', 'hanmail.net'),
            ('nate.com', 'nate.com'),
            ('hotmail.com', 'hotmail.com'),
            ('yahoo.com', 'yahoo.com'),
            ('kakao.com', 'kakao.com'),
            ('icloud.com', 'icloud.com'),
            ('outlook.com', 'outlook.com'),
            ('custom', '직접 입력')
        ],
        widget=forms.Select(attrs={'class': 'form-select email-domain-select'}),
        required=True
    )
    custom_domain = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '도메인을 입력하세요'}),
        label='직접 입력 도메인'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호 입력'}),
        max_length=4,
        min_length=4,
        required=True,
        label='비밀번호 (숫자 4자리)',
        error_messages={
            'min_length': '비밀번호는 4자리여야 합니다.',
            'max_length': '비밀번호는 4자리여야 합니다.',
            'invalid': '비밀번호는 숫자 4자리여야 합니다.'
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호 확인'}),
        max_length=4,
        min_length=4,
        required=True,
        label='비밀번호 확인'
    )
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '주소 입력'}),
        required=True,
        label='주소'
    )
    detailed_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '상세 주소 입력'}),
        required=False, # 필수 항목에서 제외
        label='상세 주소'
    )
    business_type = forms.MultipleChoiceField(
        choices=[
            ('노인복지사', '노인복지사'),
            ('사회복지사', '사회복지사'),
            ('간호사', '간호사'),
            ('의료기술사', '의료기술사'),
            ('치매전문가', '치매전문가'),
            ('노인케어 전문가', '노인케어 전문가'),
            ('재활치료사', '재활치료사'),
            ('기타', '기타'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False, # 필수 항목에서 제외
        label='업종 선택'
    )
    # 이름과 성 추가
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이름 입력'}),
        label='이름'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '성 입력'}),
        label='성'
    )
    phone_number = forms.CharField(
        required=True,
        label='전화번호',
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '전화번호를 입력하세요'}),
        validators=[
            RegexValidator(
                regex=r'^\d{2,3}-\d{3,4}-\d{4}$',
                message='전화번호는 형식에 맞게 입력해야 합니다. 예: 010-1234-5678'
            )
        ]
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "비밀번호가 일치하지 않습니다.")

        if password1 and (not password1.isdigit() or len(password1) != 4):
            self.add_error('password1', "비밀번호는 숫자 4자리여야 합니다.")

        return cleaned_data
