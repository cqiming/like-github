from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Repository
from .forms import RepositoryForm
import subprocess
from pathlib import Path
from django.conf import settings
import json
from django.views.decorators.http import require_http_methods

def get_git_info(repo_path, path=''):
    """获取Git仓库信息"""
    try:
        # 获取提交记录
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        commits = result.stdout.decode('utf-8').strip().split('\n') if result.stdout else []
        
        # 获取分支
        result = subprocess.run(
            ['git', 'branch', '-r'], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        branches = result.stdout.decode('utf-8').strip().split('\n') if result.stdout else []
        
        # 获取文件列表 - 对于bare仓库，需要指定分支
        tree_path = 'HEAD'
        if path:
            tree_path = f'HEAD:{path}'
        
        result = subprocess.run(
            ['git', 'ls-tree', tree_path], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        files = []
        folders = []
        
        if result.stdout:
            lines = result.stdout.decode('utf-8').strip().split('\n')
            for line in lines:
                if line:
                    parts = line.split()
                    if len(parts) >= 4:
                        mode = parts[0]
                        obj_type = parts[1]
                        obj_hash = parts[2]
                        name = ' '.join(parts[3:])
                        
                        if obj_type == 'tree':  # 文件夹
                            folders.append({
                                'name': name,
                                'path': f"{path}/{name}" if path else name
                            })
                        elif obj_type == 'blob':  # 文件
                            files.append({
                                'name': name,
                                'path': f"{path}/{name}" if path else name
                            })
        
        return {
            'commits': commits,
            'branches': branches,
            'files': files,
            'folders': folders,
            'has_content': len(commits) > 0,
            'current_path': path
        }
    except Exception as e:
        return {'commits': [], 'branches': [], 'files': [], 'folders': [], 'has_content': False, 'error': str(e)}

def get_file_content(repo_path, file_path):
    """获取文件内容"""
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD:{file_path}'], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            return result.stdout.decode('utf-8')
        else:
            return f"Error: {result.stderr.decode('utf-8')}"
    except Exception as e:
        return f"Error: {str(e)}"

# 前端视图
@login_required
def repository_list(request):
    """仓库列表页面"""
    repositories = Repository.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'repositories/repository_list.html', {
        'repositories': repositories
    })

@login_required
def create_repository(request):
    """创建仓库页面"""
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repository = form.save(commit=False)
            repository.owner = request.user
            repository.is_public = request.POST.get('visibility') == 'public'
            repository.save()
            messages.success(request, f'仓库 "{repository.name}" 创建成功！')
            # 明确指定前端页面的URL
            return redirect('/repositories/{}/'.format(repository.id))
    else:
        form = RepositoryForm()
    
    return render(request, 'repositories/create_repository.html', {
        'form': form
    })

@login_required
def repository_detail(request, repo_id):
    """仓库详情页面"""
    repository = get_object_or_404(Repository, id=repo_id)
    
    # 检查权限
    if not repository.is_public and repository.owner != request.user:
        messages.error(request, '您没有权限访问此仓库')
        return redirect('repositories')
    
    # 获取路径参数
    path = request.GET.get('path', '')
    file_path = request.GET.get('file', '')
    
    # 获取Git仓库信息
    repo_path = Path(settings.BASE_DIR) / 'repositories' / 'repositories'  / repository.owner.username / repository.name
    git_info = {}
    file_content = None
    
    if repo_path.exists():
        git_info = get_git_info(repo_path, path)
        
        # 如果请求查看文件内容
        if file_path:
            file_content = get_file_content(repo_path, file_path)
        
        # 添加调试信息
        print(f"Repository path: {repo_path}")
        print(f"Current path: {path}")
        print(f"Git info: {git_info}")
    else:
        print(f"Repository path does not exist: {repo_path}")
    
    # 处理路径分割，用于构建返回上级目录的链接
    path_parts = path.split('/') if path else []
    parent_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
    
    return render(request, 'repositories/repository_detail.html', {
        'repository': repository,
        'git_info': git_info,
        'file_content': file_content,
        'current_path': path,
        'file_path': file_path,
        'path_parts': path_parts,
        'parent_path': parent_path
    })

@login_required
def edit_repository(request, repo_id):
    """编辑仓库页面"""
    repository = get_object_or_404(Repository, id=repo_id, owner=request.user)
    
    if request.method == 'POST':
        form = RepositoryForm(request.POST, instance=repository)
        if form.is_valid():
            repository = form.save(commit=False)
            repository.is_public = request.POST.get('visibility') == 'public'
            repository.save()
            messages.success(request, '仓库信息更新成功！')
            # 明确指定前端页面的URL
            return redirect('/repositories/{}/'.format(repository.id))
    else:
        form = RepositoryForm(instance=repository)
    
    return render(request, 'repositories/edit_repository.html', {
        'form': form,
        'repository': repository
    })

@login_required
@require_http_methods(["POST"])
def save_file(request, repo_id):
    """保存文件内容"""
    try:
        repository = get_object_or_404(Repository, id=repo_id, owner=request.user)
        
        data = json.loads(request.body)
        file_path = data.get('file_path')
        content = data.get('content')
        
        if not file_path or content is None:
            return JsonResponse({'success': False, 'error': '缺少文件路径或内容'})
        
        # 获取仓库路径
        repo_path = Path(settings.BASE_DIR) / 'repositories' / 'repositories' / repository.owner.username / repository.name
        
        if not repo_path.exists():
            return JsonResponse({'success': False, 'error': '仓库不存在'})
        
        # 创建临时文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 使用git命令更新文件
            result = subprocess.run(
                ['git', 'hash-object', '-w', temp_file_path],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                return JsonResponse({'success': False, 'error': '文件哈希计算失败'})
            
            file_hash = result.stdout.decode('utf-8').strip()
            
            # 更新索引
            result = subprocess.run(
                ['git', 'update-index', '--add', '--cacheinfo', '100644', file_hash, file_path],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                return JsonResponse({'success': False, 'error': '索引更新失败'})
            
            # 提交更改
            result = subprocess.run(
                ['git', 'commit', '-m', f'Update {file_path} via web interface'],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                return JsonResponse({'success': False, 'error': '提交失败'})
            
            return JsonResponse({'success': True})
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
