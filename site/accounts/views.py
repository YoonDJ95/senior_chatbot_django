# C:\go\site\accounts\views.py
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm  # 임포트
from .forms import SignupForm
from .models import Profile

def signup_view(request): 
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # 이메일 입력 처리
            email_id = form.cleaned_data['email_id'].strip()
            email_domain = form.cleaned_data['email_domain'].strip()
            custom_domain = form.cleaned_data.get('custom_domain', '').strip()

            # 이메일 결합
            if email_domain == 'custom' and custom_domain:
                full_email = f"{email_id}@{custom_domain}"  # custom 도메인 입력 시 '@' 추가
            else:
                full_email = f"{email_id}@{email_domain}"  # 선택된 도메인에도 '@' 추가

            # 이메일 중복 확인
            if User.objects.filter(username=full_email).exists():
                form.add_error('email_id', '이미 사용 중인 이메일입니다.')
                return render(request, 'signup.html', {'form': form})

            # 사용자 정보 추출
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name'].strip()
            last_name = form.cleaned_data['last_name'].strip()
            phone_number = form.cleaned_data.get('phone_number', '').strip()
            address = form.cleaned_data['address'].strip()
            detailed_address = form.cleaned_data['detailed_address'].strip()
            business_types = form.cleaned_data.get('business_type', [])  # 체크박스가 선택되지 않았을 경우 빈 리스트를 반환

            # 사용자 생성 및 예외 처리
            try:
                # User 객체 생성
                user = User.objects.create_user(
                    username=full_email,  # 사용자 ID로 이메일 사용
                    password=password,
                    email=full_email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Profile 생성 및 주소와 업종 저장
                Profile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    address=address,
                    detailed_address=detailed_address,
                    business_types=business_types  # 선택된 업종 저장
                )

                # 자동 로그인 처리
                auth_login(request, user)
                return redirect('home')
            
            except Exception as e:
                # 예외 발생 시 오류 메시지 표시
                form.add_error(None, f'회원가입 중 오류가 발생했습니다: {str(e)}')
                return render(request, 'signup.html', {'form': form})
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})



def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Django 내장 로그인 함수
            return redirect('home')  # 로그인 성공 시 홈으로 리디렉션
        else:
            return render(request, 'login.html', {'form': form})  # 실패 시 폼에 오류 표시
    else:
        form = AuthenticationForm()  # 빈 폼을 전달
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth.logout(request)
    return redirect('home')

def home(request):
    return render(request, 'chatbot/home.html')
