from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Issue, IssueComment, IssueLabel, Milestone
from repositories.models import Repository

@login_required
def issue_list(request, repo_id):
    """仓库Issue列表"""
    repository = get_object_or_404(Repository, id=repo_id)
    issues = repository.issues.all().order_by('-created_at')
    # 预计算开启/关闭的 issue 数量，避免在模板中调用带参数的方法
    open_count = issues.filter(is_open=True).count()
    closed_count = issues.filter(is_open=False).count()

    return render(request, 'issues/issue_list.html', {
        'repository': repository,
        'issues': issues,
        'open_count': open_count,
        'closed_count': closed_count,
    })

@login_required
def issue_detail(request, repo_id, issue_id):
    """Issue详情"""
    repository = get_object_or_404(Repository, id=repo_id)
    issue = get_object_or_404(Issue, id=issue_id, repository=repository)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            IssueComment.objects.create(
                issue=issue,
                user=request.user,
                content=content
            )
            messages.success(request, '评论添加成功！')
            return redirect('issue_detail', repo_id=repo_id, issue_id=issue_id)
    
    return render(request, 'issues/issue_detail.html', {
        'repository': repository,
        'issue': issue
    })

@login_required
def create_issue(request, repo_id):
    """创建Issue"""
    repository = get_object_or_404(Repository, id=repo_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        issue_type = request.POST.get('type', 'issue')
        
        if title and content:
            issue = Issue.objects.create(
                title=title,
                content=content,
                type=issue_type,
                creator=request.user,
                repository=repository
            )
            messages.success(request, f'{issue.get_type_display()}创建成功！')
            return redirect('issue_detail', repo_id=repo_id, issue_id=issue.id)
    
    return render(request, 'issues/create_issue.html', {
        'repository': repository
    })
