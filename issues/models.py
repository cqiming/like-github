from django.db import models
from users.models import User
from repositories.models import Repository

# Create your models here.

class IssueLabel(models.Model):
    name = models.CharField(max_length=32, verbose_name='标签名')
    color = models.CharField(max_length=7, default='#cccccc', verbose_name='颜色')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='labels')

    def __str__(self):
        return self.name

class Milestone(models.Model):
    title = models.CharField(max_length=100, verbose_name='里程碑标题')
    description = models.TextField(blank=True, verbose_name='描述')
    due_date = models.DateField(null=True, blank=True, verbose_name='截止日期')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='milestones')
    is_closed = models.BooleanField(default=False, verbose_name='已关闭')

    def __str__(self):
        return self.title

class Issue(models.Model):
    ISSUE = 'issue'
    PR = 'pr'
    TYPE_CHOICES = ((ISSUE, 'Issue'), (PR, 'Pull Request'))
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_issues')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='issues')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=ISSUE, verbose_name='类型')
    labels = models.ManyToManyField(IssueLabel, blank=True, related_name='issues')
    milestone = models.ForeignKey(Milestone, null=True, blank=True, on_delete=models.SET_NULL, related_name='issues')
    is_open = models.BooleanField(default=True, verbose_name='开启')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"

class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
