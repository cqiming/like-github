from django.db import models
from users.models import User

class Repository(models.Model):
    name = models.CharField(max_length=100, verbose_name='仓库名')
    description = models.TextField(blank=True, verbose_name='描述')
    is_public = models.BooleanField(default=True, verbose_name='公开')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories', verbose_name='所有者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        unique_together = ('name', 'owner')
        verbose_name = '仓库'
        verbose_name_plural = '仓库'

    def __str__(self):
        return f'{self.owner.username}/{self.name}'

class Collaborator(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=20, default='write', choices=(('read','只读'),('write','写入'),('admin','管理员')))
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('repository', 'user')

class Release(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='releases')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tag_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('repository', 'tag_name')

class WikiPage(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='wikis')
    title = models.CharField(max_length=100)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('repository', 'title')
