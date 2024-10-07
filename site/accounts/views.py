# C:\go\site\accounts\views.py
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate

def signup_view(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            # 사용자 생성
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1'],
                email=request.POST['email'],
            )
            # 자동 로그인
            auth.login(request, user)
            # 홈 페이지로 리디렉션
            return redirect('/')
        else:
            # 비밀번호 불일치 에러 메시지와 함께 폼 다시 렌더링
            return render(request, 'signup.html', {'error': '비밀번호가 일치하지 않습니다.', 'kakao_api_key': settings.KAKAO_API_KEY})
    return render(request, 'signup.html', {'kakao_api_key': settings.KAKAO_API_KEY})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')  # 로그인이 성공하면 게시판으로 리디렉션
        else:
            return render(request, 'login.html', {'error': 'username or password is incorrect.'})  # 경로 수정
    else:
        return render(request, 'login.html')  # 경로 수정

def logout(request):
    auth.logout(request)
    return redirect('home')

def home(request):
    return render(request, 'chatbot/home.html')
