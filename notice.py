# 장고 설치 및 가상화 실행~
# https://wikidocs.net/70649
# VSCode 터미널 출력
# cmd에서 입력할것.
"cd.." # 상위폴더로 이동
"mkdir go" # go라는 폴더를 생성
"cd go" # 해당경로내에서 해당 이름(go)의 폴더로 이동
"python -m venv mysite" # 가상화 작업

"mysite/Scripts 경로에서 activate 입력" # 가상화로 이동함. (mysite) 나옴
"(mysite) pip install django" # 장고 설치

"cd '\'" # 최상위경로 이동
"(site경로에) django-admin startproject config ." # site라는 폴더 밑에 config 항목 설치
"python manage.py runserver" # 가상서버 실행
"ctrl+c 또는 deactivate" # 가상서버 해제

"(site경로에) django-admin startapp app" #

"path('pybo', views.index)," #urls.py 에서 경로 지정해주기

# 하기 두 경로 상호간 동작.
"go/site/app/views.py"  
"go/site/config/urls.py"


"C:\go\mysite\Scripts\activate.bat" # 가상화 실행
"python manage.py runserver" # 가상서버 실행

"pip install -r requirements.txt" # requirements.txt 안에 있는 요소 설치


"git rm -r --cached 항목명/" #깃에 해당 항목 추적 제외