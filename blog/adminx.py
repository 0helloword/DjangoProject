from django.contrib import admin

# Register your models here.
import xadmin
from blog.models import Article, User, Tag
from xadmin import views


class ArticleAdmin(object):
    #定制管理后台内容的显示列
    list_display=['title','tags','click_num','love_num','user']
    #增加管理后台查询搜索框
    search_fields=['title','id']
    #设置可编辑项
    list_editable=['click_num','love_num']
    #设置过滤器
    list_filter=['user']


xadmin.site.register(Article,ArticleAdmin)
# xadmin.site.register(User)
xadmin.site.register(Tag)

#定制主题
class BaseSettings(object):
    enable_themes=True
    use_bootswatch=True

#更改全局参数
class GlobalSetting(object):
    site_title='博客后台管理'
    site_footer='小拉的博客公司'

xadmin.site.register(views.BaseAdminView,BaseSettings)
xadmin.site.register(views.CommAdminView,GlobalSetting)