from django.urls import path
from . import views

urlpatterns = [
    path('search/repositories/', views.repository_search, name='repository_search'),
    path('search/users/', views.user_search, name='user_search'),
    path('search/code/', views.code_search, name='code_search'),
] 