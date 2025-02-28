"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# C:\go\site\config\urls.py

from django.contrib import admin
from django.urls import path
from app.views import chatbot_response, index, get_kakao_api_key, job_detail_view,home,resume_view,resume_success # 새로운 뷰 추가
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot/', chatbot_response, name='chatbot_response'),  # 챗봇 API 경로
    path('get_kakao_api_key/', get_kakao_api_key, name='get_kakao_api_key'),  # 카카오 API 키 반환
    path('job_detail/<str:job_id>/', job_detail_view, name='job_detail_view'),  # 상세 정보 조회 경로 추가
    path('', home, name='home'),  # 기본페이지
    path('index/', index, name='chatbot_index'),  # 일자리 차기
    path('accounts/', include('accounts.urls')),
    path('save-search-history/', views.save_search_history, name='save_search_history'),
    path('search-history/', views.search_history, name='search_history'),
    path('clear-search-history/', views.clear_search_history, name='clear_search_history'),
    path('save_transcript/', views.save_transcript, name='save_transcript'),
    path('toggle_recording/', views.toggle_recording, name='toggle_recording'),
    path('resume/', resume_view, name='resume'),
    path('resume/success/', resume_success, name='resume_success'),  # 이력서 저장 성공 페이지
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
