from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Follow, Star, Watch, Activity
from users.models import User
from repositories.models import Repository

@login_required
def follow_user(request, user_id):
    """关注用户"""
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        messages.success(request, f'已关注 {user_to_follow.username}')
    return redirect('user_profile', username=user_to_follow.username)

@login_required
def unfollow_user(request, user_id):
    """取消关注用户"""
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'已取消关注 {user_to_unfollow.username}')
    return redirect('user_profile', username=user_to_unfollow.username)

@login_required
def star_repository(request, repo_id):
    """Star仓库"""
    repository = get_object_or_404(Repository, id=repo_id)
    Star.objects.get_or_create(user=request.user, repository=repository)
    return JsonResponse({'success': True})

@login_required
def unstar_repository(request, repo_id):
    """取消Star仓库"""
    repository = get_object_or_404(Repository, id=repo_id)
    Star.objects.filter(user=request.user, repository=repository).delete()
    return JsonResponse({'success': True})

@login_required
def watch_repository(request, repo_id):
    """Watch仓库"""
    repository = get_object_or_404(Repository, id=repo_id)
    Watch.objects.get_or_create(user=request.user, repository=repository)
    return JsonResponse({'success': True})

@login_required
def unwatch_repository(request, repo_id):
    """取消Watch仓库"""
    repository = get_object_or_404(Repository, id=repo_id)
    Watch.objects.filter(user=request.user, repository=repository).delete()
    return JsonResponse({'success': True})

@login_required
def activity_feed(request):
    """用户动态流"""
    # 获取关注用户的动态
    following_users = [f.following for f in request.user.following.all()]
    activities = Activity.objects.filter(user__in=following_users).order_by('-created_at')[:20]
    
    return render(request, 'social/activity_feed.html', {
        'activities': activities
    })
