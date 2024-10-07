# accounts/urls.py
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('home/login/', login, name='login'),
    path('home/logout/', logout, name='logout'),
    path('home/', home, name='home'),
]