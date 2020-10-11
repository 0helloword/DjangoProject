from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nickname = models.CharField('昵称', max_length=100, blank=True)
    phone = models.CharField("手机号码", max_length=15, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='标签名')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tag'
        verbose_name = '标签表'
        verbose_name_plural = '标签表'


class Article(models.Model):
    title = models.CharField(verbose_name='标题', max_length=100)
    decs = models.CharField(verbose_name='简介', max_length=256)
    # content = models.TextField(verbose_name='内容')
    #使用ckeditor富文本
    content=RichTextUploadingField(verbose_name='内容')
    date = models.DateField(verbose_name='发表日期', auto_now=True)
    click_num = models.IntegerField(verbose_name='浏览量', default=0)
    love_num = models.IntegerField(verbose_name='点赞数', default=0)
    image = models.ImageField(verbose_name='文章图片', upload_to='upload/article/%Y/%M',default='upload/article/2020/05/1.jpg')

    tags = models.ManyToManyField(to=Tag,verbose_name='标签')  # 多对多随意定义在哪边
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,verbose_name='用户')  # 一对多定义在多

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'article'
        verbose_name = '文章表'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    nickname=models.CharField(max_length=50,verbose_name='昵称')
    date=models.DateTimeField(auto_now=True,verbose_name='评论时间')
    content=models.TextField(verbose_name='内容')
    article=models.ForeignKey(to=Article,on_delete=models.CASCADE,verbose_name='文章')
    def __str__(self):
        return self.nickname
    class Meta:
        db_table='comment'
        verbose_name='评论表'
        verbose_name_plural=verbose_name

class Message(models.Model):
    nickname=models.CharField(max_length=50,verbose_name='昵称')
    date=models.DateTimeField(auto_now=True,verbose_name='留言时间')
    content=models.TextField(verbose_name='内容')
    icon=models.CharField(max_length=256,verbose_name='头像')

    def __str__(self):
        return self.nickname
    class Meta:
        db_table='message'
        verbose_name='留言表'
        verbose_name_plural=verbose_name