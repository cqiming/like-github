from django.urls import path, include
from .git_protocol import git_upload_pack, git_receive_pack, git_info_refs, init_repository_git, git_repository_redirect

urlpatterns = [
    # 处理.git后缀的URL（支持带路径）- 必须放在前面
    path('<str:username>/<str:repo_name>.git/<path:rest>', git_repository_redirect, name='git_repository_redirect'),
    path('<str:username>/<str:repo_name>.git', git_repository_redirect, name='git_repository_redirect_simple'),
    # Git协议路由
    path('<str:username>/<str:repo_name>/info/refs', git_info_refs, name='git_info_refs'),
    path('<str:username>/<str:repo_name>/git-upload-pack', git_upload_pack, name='git_upload_pack'),
    path('<str:username>/<str:repo_name>/git-receive-pack', git_receive_pack, name='git_receive_pack'),
    path('<str:username>/<str:repo_name>/init', init_repository_git, name='init_repository_git'),
] 