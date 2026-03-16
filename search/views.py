from django.shortcuts import render
from repositories.models import Repository
from users.models import User

# 仓库搜索

def repository_search(request):
    query = request.GET.get('q', '')
    results = Repository.objects.filter(name__icontains=query) if query else []
    return render(request, 'search/repository_search.html', {'query': query, 'results': results})

# 用户搜索

def user_search(request):
    query = request.GET.get('q', '')
    results = User.objects.filter(username__icontains=query) if query else []
    return render(request, 'search/user_search.html', {'query': query, 'results': results})

# 代码搜索（仅骨架，实际需遍历文件内容）
def code_search(request):
    query = request.GET.get('q', '')
    # TODO: 实现代码内容搜索
    results = []
    return render(request, 'search/code_search.html', {'query': query, 'results': results})
