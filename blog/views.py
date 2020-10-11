from captcha.models import CaptchaStore
from captcha.views import captcha_refresh
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from blog.forms import ZhuceForm, RegisterForm, LoginForm, CaptchaTestForm, UpdatepwdForm, ArticleForm, \
    CaptchaCommentForm
from blog.models import User, Article, Tag, Comment, Message
from utils import util_sendmsg, send_email


def user_login(request):
    if request.method == 'GET':
        lform = LoginForm()
        return render(request, 'login.html', context={'lform': lform})
    else:
        lform = LoginForm(request.POST)
        if lform.is_valid():
            username = lform.cleaned_data.get('username')
            password = lform.cleaned_data.get('password')
            # 方法一：通用
            # user=User.objects.filter(username=username).first()
            # flag=check_password(password,user.password)
            # if flag:
            #     request.session['username']=username
            #     return redirect(reverse('blog:index'))
            # else:
            #     return render(request, 'login.html', context={'lform': lform,'msg':'用户名或密码错误'})
            # 方法二：使用自带的login方法，适用于user继承自AbstractUser
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect(reverse('blog:index'))
        return render(request, 'login.html', context={'lform': lform})


# 使用modelform,跟模型关联，不需要一个个字段去定义
def register(request):
    if request.method == 'GET':
        rform = RegisterForm()
        return render(request, 'register.html', context={'rform': rform})
    else:
        # 使用form获取数据
        rform = RegisterForm(request.POST)
        if rform.is_valid():  # 进行数据的校验
            print(rform.cleaned_data)
            username = rform.cleaned_data.get('username')
            password = rform.cleaned_data.get('password')
            phone = rform.cleaned_data.get('phone')
            email = rform.cleaned_data.get('email')
            # 判断用户名或手机号是否存在
            if not User.objects.filter(Q(username=username) | Q(phone=phone)).exists():
                password = make_password(password)
                user = User.objects.create(username=username, password=password, phone=phone, email=email)
                if user:
                    return redirect(reverse('blog:login'))
            else:
                return render(request, 'register.html', context={'rform': rform, 'msg': '用户名或手机号已存在'})
        return render(request, 'register.html', context={'rform': rform, 'msg': '注册失败'})


# 使用form
def zhuce(request):
    if request.method == 'GET':
        rform = ZhuceForm()
        return render(request, 'zhuce.html', context={'rform': rform})
    else:
        rform = ZhuceForm(request.POST)
        if rform.is_valid():
            print(rform.cleaned_data)
            username = rform.cleaned_data.get('username')  # 从校验通过的数据中获取对应的参数值
            password = rform.cleaned_data.get('password')
            phone = rform.cleaned_data.get('phone')
            user = User()
            user.username = username
            user.password = password
            user.phone = phone
            user.save()
        else:
            return render(request, 'zhuce.html', context={'rform': rform})
        return HttpResponse('注册成功')


def user_logout(request):
    # 方法一：
    # request.session.clear()#删除字典
    # 方法二：
    # request.session.flush()#删除django_session+cookie+字典
    # return redirect(reverse('blog:login'))
    # 方法三：使用自带的退出方法
    logout(request)
    return redirect(reverse('blog:login'))

#首页，分页显示所有的文章
def index(request):
    tags=Tag.objects.all()
    tagid=request.GET.get('tagid',"")#获取tagid值，如果没有给一个默认值，为空
    #如果传了tagid则根据tagid筛选对应的文章列表，否则显示所有的文章
    if tagid:
        tag=Tag.objects.get(pk=tagid)
        articles=tag.article_set.all()
    else:
        articles = Article.objects.all().order_by('-click_num')
    paginator=Paginator(articles,3)#实现分页，每页3条数据
    # print(paginator.count)#总记录数
    # print(paginator.num_pages)#总的页码数
    # print(paginator.page_range)#每页的记录范围
    #方法 get_page()
    page=request.GET.get('page',1)#获取页码数，不传页码默认为1
    page=paginator.get_page(page)#返回一个page对象
    # page.has_next()#判断是否存在后一页
    # page.has_previous()#判断是否存在前一页
    # page.next_page_number()#获取下一页的页码数
    # page.previous_page_number()#获取前一页的页码数
    #属性
    # page.object_list 获取当前页的所有对象
    # page.number  获取当前页的页码数
    # page.paginator 分页器对象
    return render(request, 'index.html', context={'page': page,'tags':tags,'tagid':tagid})


# 发送验证码路由 ajax发过来的请求
@csrf_exempt
def sendmsg(request):
    phone = request.GET.get('phone')
    result = util_sendmsg(phone)
    status = result.get('code')
    data = {}
    if status == 200:
        check_code = result.get('obj')  # 获取短信验证码
        print(check_code)
        # 使用session保存验证码
        request.session[phone] = check_code
        data['status'] = 200
        data['msg'] = '验证码发送成功'
    else:
        data['status'] = 500
        data['msg'] = '验证码发送失败'
    return JsonResponse(data=data)


# 手机短信验证码登陆
def code_login(request):
    if request.method == 'GET':
        return render(request, 'codelogin.html')
    else:
        code = request.POST.get('code')
        phone = request.POST.get('phone')
        # 从session中获取网易云信发送的验证码
        check_code = request.session.get(phone)
        print(code, check_code)
        if code == check_code:
            user = User.objects.filter(phone=phone).first()
            # 直接调自带的login,获取用户名，显示在index页面
            if user:
                login(request, user)
                return redirect(reverse('blog:index'))
        else:
            return render(request, 'codelogin.html', context={'msg': '验证码错误'})


# 忘记密码，页面中使用了图像验证码
# 使用js实现了刷新验证码，校验验证码
def forget_pwd(request):
    if request.method == 'GET':
        form = CaptchaTestForm()
        return render(request, 'forget_pwd.html', context={'form': form})
    else:
        # 获取提交的邮箱，发送验证邮件,通过邮箱链接设置新的密码
        email = request.POST.get('email')
        print(email)
        # 给此邮箱地址发邮件
        result = send_email(email, request)
        if result:
            return HttpResponse("已成功发送找回密码邮件,请去邮箱更改密码，<a href='/blog/index/'>返回首页</a>")


# 更新密码
def update_pwd(request):
    if request.method == 'GET':
        code = request.GET.get('c')  # 将code传到表单中的一个隐藏元素中，然后一起提交给后端
        form = UpdatepwdForm()
        return render(request, 'update_pwd.html', context={'form': form, 'code': code})
    else:
        code = request.POST.get('code')  # 获取隐藏的code值
        user_id = request.session.get(code)
        user = User.objects.get(pk=user_id)
        password = request.POST.get('password')
        user.password = make_password(password)
        user.save()
        return redirect(reverse('blog:login'))


# 定义一个路由验证图形验证码
def valide_code(request):
    if request.is_ajax():
        key = request.GET.get('key')  # 获取图形验证码的value值
        code = request.GET.get('code')  # 获取用户输入的验证码
        captcha = CaptchaStore.objects.filter(hashkey=key).first()  # 在CaptchaStore表中根据value值找到对应的图形验证码对象
        print(key, code)
        if captcha.response == code.lower():  # response属性值为图形验证码的值，判断用户输入的验证码是否与该值一致
            data = {'status': 1}
        else:
            data = {'status': 0}
        return JsonResponse(data)


# 使用装饰器判断用户是否登陆,需在setting中添加LOGIN_URL
@login_required
def mine(request):
    return render(request, 'mine.html')

#文章详情
def detail(request):
    id = request.GET.get('id')
    article = Article.objects.get(pk=id)
    article.click_num += 1
    article.save()
    #获取文章下的评论
    comments=Comment.objects.filter(article_id=id)
    c_count=comments.count()
    print(comments.count())
    # 获取文章关联的所有标签
    tags = article.tags.all()
    # 获取标签下关联的所有文章
    article_list = []
    for tag in tags:
        article_list += tag.article_set.all()
    # 去重-去掉不同标签下的相同文章，仅保留一个
    article_list = list(set(article_list))
    # 去除当前详情页的文章
    for a in article_list:
        if a.id == article.id:
            article_list.remove(a)  # 按值删除
    print(article_list)
    min_id = Article.objects.first().id
    max_id = Article.objects.last().id
    print(min_id, max_id)
    cform=CaptchaCommentForm()
    if article.id == min_id:#当文章id为最小值，即为第一篇时，不显示上一篇的链接
        up_id = 0
        down_id = article.id + 1
        down_title = Article.objects.get(pk=down_id).title
        return render(request, 'detail.html',
                      context={'article': article, 'article_list': article_list, 'up_id': up_id, 'down_id': down_id,
                               'down_title': down_title,'cform':cform,'comments':comments,'c_count':c_count})
    elif article.id == max_id:#当文章id为最大值，即为最后一篇时，不显示下一篇的链接
        down_id = 0
        up_id = article.id - 1
        up_title = Article.objects.get(pk=up_id).title
        return render(request, 'detail.html',
                      context={'article': article, 'article_list': article_list, 'up_id': up_id, 'down_id': down_id,
                               up_id: 'up_id', 'up_title': up_title,'cform':cform,'comments':comments,'c_count':c_count})
    elif article.id > min_id and article.id < max_id:#当文章id为中间值时，显示上一篇和下一篇的链接
        up_id = article.id - 1
        down_id = article.id + 1
        up_title = Article.objects.get(pk=up_id).title
        down_title = Article.objects.get(pk=down_id).title
        return render(request, 'detail.html',
                      context={'article': article, 'article_list': article_list, 'up_id': up_id, 'down_id': down_id,
                               'up_title': up_title, 'down_title': down_title,'cform':cform,'comments':comments,'c_count':c_count})


def write(request):
    if request.method=='GET':
        aform=ArticleForm()
        return render(request,'write.html',context={'aform':aform})
    else:
        aform=ArticleForm(request.POST)
        print(aform)
        if aform.is_valid():
            data=aform.cleaned_data
            article=Article()
            article.title=data.get('title')
            article.desc = data.get('desc')
            article.content = data.get('content')
            article.image = data.get('image')
            article.user = data.get('user')#1对多，可直接赋值
            article.save()
            article.tags.set(data.get('tags'))#多对多，必须文章生成后有了文章id才能添加标签
            return redirect(reverse('blog:index'))
        else:
            print('校验失败')
        return HttpResponse('TEST')

@csrf_exempt
#提交评论
def comment(request):
    nickname=request.GET.get('nickname')
    content=request.GET.get('comment')
    article_id=request.GET.get('article_id')
    print(article_id,nickname,content)
    comment=Comment()
    comment.nickname=nickname
    comment.content=content
    comment.article_id=article_id
    comment.save()
    data={
        'status':200
    }
    return JsonResponse(data=data)


def message(request):
    messages = Message.objects.all().order_by('-date')
    paginator = Paginator(messages, 3)  # 实现分页，每页3条数据
    page = request.GET.get('page', 1)  # 获取页码数，不传页码默认为1
    page = paginator.get_page(page)  # 返回一个page对象
    if request.method=='GET':
        return render(request,'message.html',context={'messages':messages,'page':page})
    else:
        nickname=request.POST.get('nickname')
        mycall=request.POST.get('mycall')
        print(mycall)
        lytext=request.POST.get('lytext')
        if nickname and lytext:
            message=Message.objects.create(nickname=nickname,icon=mycall,content=lytext)
            if message:
                return redirect(reverse('blog:message'))
        return render(request,'message.html',context={'messages':messages,'errors':'必须输入用户名和评论','page':page})
