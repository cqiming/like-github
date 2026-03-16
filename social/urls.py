from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('users/<int:user_id>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('repositories/<int:repo_id>/star/', views.star_repository, name='star_repository'),
    path('repositories/<int:repo_id>/unstar/', views.unstar_repository, name='unstar_repository'),
    path('repositories/<int:repo_id>/watch/', views.watch_repository, name='watch_repository'),
    path('repositories/<int:repo_id>/unwatch/', views.unwatch_repository, name='unwatch_repository'),
    path('activity/', views.activity_feed, name='activity_feed'),
] 