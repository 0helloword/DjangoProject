import re

from captcha.fields import CaptchaField
from ckeditor.fields import RichTextFormField
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, EmailField
from blog.models import User, Article


# 继承form,前端想展示哪些字段就设置哪些字段
class ZhuceForm(Form):
    username = forms.CharField(label='username', max_length=10, min_length=3, required=True,
                               error_messages={'min_length': '用户名至少3位', })
    password = forms.CharField(label='password', max_length=10, required=True, error_messages={'required': '密码不能为空', },
                               widget=forms.widgets.PasswordInput)  # 使用widget插件设置密码格式
    phone = forms.CharField(label='phone', min_length=11, required=True, error_messages={'required': '手机号码不能为空', })

    # 校验用户名的规则
    def clean_username(self):
        print(111)
        username = self.cleaned_data.get('username')
        # 姓名只能以字母开头,长度大于3
        result = re.match(r'[A-Za-z]\w{2,}', username)
        if not result:
            raise ValidationError('用户名必须以字母开头')
        return username

# 继承ModelForm,前端想展示哪些字段直接跟model绑定，无需一个个去定义
class RegisterForm(ModelForm):
    #如数据库中没有这个字段，直接在这里加上
    repassword=forms.CharField(label='确认密码',max_length=10,required=True,error_messages={'required':'密码不能为空',},widget=forms.widgets.PasswordInput)#使用widget插件设置密码格式
    class Meta:
        model=User
        fields=['username','password','repassword','phone','email']
        # fields='__all__'

    #校验用户名的规则
    def clean_username(self):
        username=self.cleaned_data.get('username')
        #姓名只能以字母开头,长度大于3
        result=re.match(r'[A-Za-z]\w{2,}',username)
        if not result:
            raise ValidationError('用户名必须以字母开头')
        return username

class LoginForm(Form):
    username = forms.CharField(label='username', max_length=10, min_length=3, required=True,
                               error_messages={'min_length': '用户名至少3位', })
    password = forms.CharField(label='password', max_length=10, required=True, error_messages={'required': '密码不能为空', },
                               widget=forms.widgets.PasswordInput)  # 使用widget插件设置密码格式

    def clean_username(self):
        username=self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError('用户名不存在')
        return username

#图形验证码,通过邮箱找回密码
class CaptchaTestForm(forms.Form):
    email = EmailField(label='邮箱',required=True)
    captcha = CaptchaField(label='验证码',required=True)

#评论显示图形验证码
class CaptchaCommentForm(forms.Form):
    nickname = forms.CharField(label='昵称',required=True)
    captcha = CaptchaField(label='验证码',required=True)
    comment=forms.CharField(label='评论',required=True)

#更新密码
class UpdatepwdForm(forms.Form):
    password=forms.CharField(label='密码',required=True)

#文章form
class ArticleForm(ModelForm):
    class Meta:
        model=Article
        fields='__all__'
        exclude=['click_num','love_num']
