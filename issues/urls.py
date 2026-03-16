from django.urls import path
from . import views

urlpatterns = [
    path('repositories/<int:repo_id>/issues/', views.issue_list, name='issue_list'),
    path('repositories/<int:repo_id>/issues/create/', views.create_issue, name='create_issue'),
    path('repositories/<int:repo_id>/issues/<int:issue_id>/', views.issue_detail, name='issue_detail'),
] 