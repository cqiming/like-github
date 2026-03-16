from django.urls import path
from .views import repository_list, create_repository, repository_detail, edit_repository, save_file

# 前端页面路由
urlpatterns = [
    path('repositories/', repository_list, name='repositories'),
    path('repositories/create/', create_repository, name='create_repository'),
    path('repositories/<int:repo_id>/', repository_detail, name='repository_detail'),
    path('repositories/<int:repo_id>/edit/', edit_repository, name='edit_repository'),
    path('repositories/<int:repo_id>/save_file/', save_file, name='save_file'),
] 