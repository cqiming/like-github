from django.db import models

# Create your models here.

class GitOperationLog(models.Model):
    action = models.CharField(max_length=50, verbose_name='操作类型')
    repository = models.CharField(max_length=100, verbose_name='仓库')
    user = models.CharField(max_length=100, verbose_name='用户')
    detail = models.TextField(verbose_name='详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='时间')

    class Meta:
        verbose_name = 'Git操作日志'
        verbose_name_plural = 'Git操作日志'
