from django.conf.urls import url

from blog import views

app_name='blog'

urlpatterns=[
    url(r'^login/',views.user_login,name='login'),
    url(r'^codelogin',views.code_login,name='codelogin'),
    url(r'^register/',views.register,name='register'),
    url(r'^zhuce/',views.zhuce,name='zhuce'),
    url(r'logout/',views.user_logout,name='logout'),
    url(r'index/',views.index,name='index'),
    url(r'sendmsg/',views.sendmsg,name='sendmsg'),
    url(r'forgetpwd/',views.forget_pwd,name='forgetpwd'),
    url(r'validecode/',views.valide_code,name='validecode'),
    url(r'^updatepwd/',views.update_pwd,name='updatepwd'),
    url(r'mine/',views.mine,name='mine'),
    url(r'detail/',views.detail,name='detail'),
    url(r'write/',views.write,name='write'),
    url(r'comment/',views.comment,name='comment'),
    url(r'message/',views.message,name='message'),


]