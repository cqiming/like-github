import os
import subprocess
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from repositories.models import Repository
import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def get_repo_path(username, repo_name):
    """获取仓库路径"""
    repos_path = Path(settings.BASE_DIR) / 'repositories'
    return repos_path / username / repo_name

def init_repository(username, repo_name):
    """初始化Git仓库"""
    try:
        repo_path = get_repo_path(username, repo_name)
        repo_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化Git仓库
        result = subprocess.run(
            ['git', 'init', '--bare'], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            logger.info(f"Initialized Git repository: {username}/{repo_name}")
            return True
        else:
            logger.error(f"Failed to initialize Git repository: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error initializing repository: {e}")
        return False

@csrf_exempt
def git_upload_pack(request, username, repo_name):
    """处理git clone/fetch请求"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        repo_path = get_repo_path(username, repo_name)
        if not repo_path.exists():
            raise Http404("Repository not found")
        
        result = subprocess.run(
            ['git', 'upload-pack', '--stateless-rpc', str(repo_path)],
            input=request.body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            response = HttpResponse(result.stdout, content_type='application/x-git-upload-pack-result')
            return response
        else:
            logger.error(f"Git upload-pack error: {result.stderr}")
            return HttpResponse(status=500)
    except Exception as e:
        logger.error(f"Error in git_upload_pack: {e}")
        return HttpResponse(status=500)

@csrf_exempt
def git_receive_pack(request, username, repo_name):
    """处理git push请求"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        repo_path = get_repo_path(username, repo_name)
        if not repo_path.exists():
            raise Http404("Repository not found")
        
        result = subprocess.run(
            ['git', 'receive-pack', '--stateless-rpc', str(repo_path)],
            input=request.body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            response = HttpResponse(result.stdout, content_type='application/x-git-receive-pack-result')
            return response
        else:
            logger.error(f"Git receive-pack error: {result.stderr}")
            return HttpResponse(status=500)
    except Exception as e:
        logger.error(f"Error in git_receive_pack: {e}")
        return HttpResponse(status=500)

def git_info_refs(request, username, repo_name):
    """处理git info/refs请求"""
    try:
        repo_path = get_repo_path(username, repo_name)
        if not repo_path.exists():
            raise Http404("Repository not found")
        
        service = request.GET.get('service', 'git-upload-pack')
        
        if service == 'git-upload-pack':
            cmd = ['git', 'upload-pack', '--advertise-refs', str(repo_path)]
        elif service == 'git-receive-pack':
            cmd = ['git', 'receive-pack', '--advertise-refs', str(repo_path)]
        else:
            return HttpResponse(status=400)
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            # 添加服务前缀
            service_line = f"# service={service}\n"
            pkt_line = f"{len(service_line) + 4:04x}{service_line}"
            data = pkt_line.encode() + b'0000' + result.stdout
            
            response = HttpResponse(data, content_type=f'application/x-{service}-advertisement')
            return response
        else:
            logger.error(f"Git info-refs error: {result.stderr}")
            return HttpResponse(status=500)
    except Exception as e:
        logger.error(f"Error in git_info_refs: {e}")
        return HttpResponse(status=500)

def init_repository_git(request, username, repo_name):
    """初始化仓库的Git环境"""
    try:
        # 检查仓库是否存在
        repo = Repository.objects.get(owner__username=username, name=repo_name)
        
        # 初始化Git仓库
        if init_repository(username, repo_name):
            return HttpResponse("Git repository initialized successfully")
        else:
            return HttpResponse("Failed to initialize Git repository", status=500)
    except Repository.DoesNotExist:
        raise Http404("Repository not found")
    except Exception as e:
        logger.error(f"Error in init_repository_git: {e}")
        return HttpResponse("Internal server error", status=500)

def git_repository_redirect(request, username, repo_name, rest=None):
    """处理.git后缀的URL"""
    try:
        # 移除.git后缀
        clean_repo_name = repo_name.replace('.git', '')
        
        # 获取service参数
        service = request.GET.get('service', 'git-upload-pack')
        
        # 构建目标URL
        if rest:
            # 如果有rest路径，直接重定向到对应路径
            target_url = f'/git/{username}/{clean_repo_name}/{rest}'
        else:
            # 重定向到info/refs
            target_url = f'/git/{username}/{clean_repo_name}/info/refs'
        
        # 添加service参数
        if service:
            target_url += f'?service={service}'
        
        logger.info(f"Redirecting from {request.path} to {target_url}")
        return redirect(target_url)
    except Exception as e:
        logger.error(f"Error in git_repository_redirect: {e}")
        return HttpResponse(f"Redirect error: {e}", status=500) 