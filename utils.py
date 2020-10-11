#向网易云信发送请求，帮助后台发送短息给用户
import hashlib
import json
import uuid
from time import time
import requests
from django.core.mail import send_mail

from blog.models import User
from blogtest.settings import EMAIL_HOST_USER

#使用网易云信发短信
def util_sendmsg(mobile):
    url="https://api.netease.im/sms/sendcode.action"
    data={'mobile':mobile}
    AppKey='b8ebda07115f76854f79c37290a70856'
    Nonce=str(time()) #使用时间戳生成随机数
    CurTime=str(time())
    AppSecret='51e0dbf8c2ea'
    content=AppSecret+Nonce+CurTime
    CheckSum=hashlib.sha1(content.encode('utf-8')).hexdigest()
    header={'AppKey':AppKey,'Nonce':Nonce,'CurTime':CurTime,'CheckSum':CheckSum}
    response=requests.post(url,data,headers=header)
    str_result=response.text #获取响应体
    json_result=json.loads(str_result)#转成json
    print(json_result)
    return json_result

#发邮件
def send_email(email,request):
    subject = '找回密码'
    user=User.objects.filter(email=email).first()
    #生成uuid，放入session中方便后面根据该id找到对应的用户--记录用户
    code=str(uuid.uuid4()).replace('-','')
    request.session[code]=user.id
    message = '''
    你好：
    此链接用于找回密码，请点击链接<a href='http://127.0.0.1:8000/blog/updatepwd?c=%s'>更新密码</a>,
              如果链接不能点击，请复制：
              http://127.0.0.1:8000/blog/updatepwd?c=%s
              个人博客团队
              '''%(code,code)

    result=send_mail(subject,"",from_email=EMAIL_HOST_USER,recipient_list=[email,],html_message=message)
    return result