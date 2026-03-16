from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# 前端视图
def user_register(request):
    """用户注册页面"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎使用Like GitHub')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    """用户登录页面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}！')
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    """用户退出登录"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('home')

@login_required
def user_profile(request):
    """用户个人资料页面"""
    return render(request, 'users/profile.html', {'user': request.user})

def home(request):
    """首页"""
    return render(request, 'home.html')
