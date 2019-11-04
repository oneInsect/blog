from django.shortcuts import render, HttpResponse, redirect
from django import forms
import json
import io
import datetime
from user_centre import models
import random
import smtplib
from email.mime.text import MIMEText
from utils import check_code as CheckCode


class SendMsgForm(forms.Form):
    email = forms.EmailField()


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32, min_length=6,
                               error_messages={'min_length': '至少需要6个字符',
                                               'max_length': '最多输入32个字符',
                                               'required': '用户名不能为空'})
    email = forms.EmailField(max_length=32,
                             error_messages={'invalid': '请输入有效邮箱',
                                             'max_length': '最多输入32个字符',
                                             'required': '邮箱不能为空'})
    email_code = forms.CharField(max_length=6,
                                 error_messages={'required': '验证码不能为空',
                                                 'max_length': '最多输入6个字符'})
    password = forms.CharField(max_length=32, min_length=6,
                               error_messages={'min_length': '至少需要6个字符',
                                               'max_length': '最多输入32个字符',
                                               'required': '密码不能为空'})


class LoginFrom(forms.Form):
    user = forms.CharField(max_length=32, min_length=6,
                           error_messages={'min_length': '至少需要6个字符',
                                           'max_length': '最多输入32个字符',
                                           'required': '用户名不能为空'})
    pwd = forms.CharField(max_length=32, min_length=6,
                          error_messages={'min_length': '至少需要6个字符',
                                          'max_length': '最多输入32个字符',
                                          'required': '密码不能为空'})
    code = forms.CharField(error_messages={'required': '验证码不能为空'})


class BaseResponse:
    def __init__(self):
        self.message = {}
        self.summary = None
        self.status = False


def random_code():
    code = ''
    for i in range(0, 4):
        current = random.randrange(0, 4)
        if current != i:
            temp = chr(random.randint(65, 90))
        else:
            temp = str(random.randint(0, 9))
        code += temp
    return code


def send_code(code):
    _user = "739056672@qq.com"
    _pwd = "cdupknupzggibbge"
    _to = "739056672@qq.com"
    print('code', code)
    msg = MIMEText(code)
    msg["Subject"] = "注册验证码"
    msg["From"] = 'chouti@live.com'
    msg["To"] = _to

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()
        print("Success!")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


def check_code(request):
    """
    获取验证码
    :param request:
    :return:
    """
    stream = io.BytesIO()
    # 创建随机字符 code
    # 创建一张图片格式的字符串，将随机字符串写到图片上
    img, code = CheckCode.create_validate_code()
    img.save(stream, "PNG")
    # 将字符串形式的验证码放在Session中
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


def index(request):
    if request.method == "GET":
        return render(request, "index.html")


def send_msg(request):
    rep = BaseResponse()
    print(request.POST)
    form = SendMsgForm(request.POST)

    if form.is_valid():
        value_dict = form.clean()
        email = value_dict['email']
        has_email_exist = models.UserInfo.objects.filter(email=email).count()
        print('jjjjj', has_email_exist)
        if has_email_exist:
            rep.summary = '此邮箱已被注册'
            return HttpResponse(json.dumps(rep.__dict__))
        current_date = datetime.datetime.now()
        code = random_code()
        count = models.SendMsg.objects.filter(email=email).count()
        print(count)
        if not count:
            models.SendMsg.objects.create(email=email, email_code=code,
                                          ctime=current_date)
            rep.status = True
        else:
            limit_time = current_date - datetime.timedelta(hours=1)
            print(limit_time)
            times = models.SendMsg.objects.filter(email=email,
                                                  ctime__gt=limit_time,
                                                  times__gt=9).count()
            print('times', times)
            if times:
                rep.summary = '请1小时后再试!'
            else:
                unfreeze = models.SendMsg.objects.filter(email=email,
                                                         ctime__lt=limit_time).count()
                if unfreeze:
                    models.SendMsg.objects.filter(email=email).update(times=0)
                from django.db.models import F
                models.SendMsg.objects.filter(email=email).update(
                    email_code=code, ctime=current_date, times=F("times") + 1)
                rep.status = True
        send_code(code)
    else:
        rep.summary = form.errors['email'][0]
        print('验证失败： ', rep.summary)
    print('返回前端： ', rep.summary)
    return HttpResponse(json.dumps(rep.__dict__))


def register(request):
    rep = BaseResponse()
    form = RegisterForm(request.POST)
    if form.is_valid():
        value_dict = form.clean()
        print(value_dict)
        current_time = datetime.datetime.now()
        limit_time = current_time - datetime.timedelta(minutes=1)

        # email_code 是否过期1分钟
        timeout = models.SendMsg.objects.filter(email=value_dict['email'],
                                                email_code=value_dict[
                                                    'email_code'],
                                                ctime__lt=limit_time).count()
        if timeout:
            rep.message['email_code'] = '验证码错误或已过期'
            return HttpResponse(json.dumps(rep.__dict__))
        has_username_exist = models.UserInfo.objects.filter(
            username=value_dict['username']).count()
        if has_username_exist:
            rep.message['username'] = '用户名已存在'
            return HttpResponse(json.dumps(rep.__dict__))
        has_email_exist = models.UserInfo.objects.filter(
            email=value_dict['email']).count()
        if has_email_exist:
            rep.message['email'] = '邮箱已存在'
            return HttpResponse(json.dumps(rep.__dict__))
        value_dict.pop('email_code')
        value_dict['ctime'] = current_time
        obj = models.UserInfo.objects.create(**value_dict)
        models.SendMsg.objects.filter(email=value_dict['email']).delete()

        user_info_dict = {'nid': obj.nid, 'email': obj.email,
                          'username': obj.username}
        request.session['is_login'] = True
        request.session['user_info'] = user_info_dict
        rep.status = True
    else:
        err_msg = form.errors.as_json()
        rep.message = json.loads(err_msg)
    print('返回前端： ', rep.message)
    return HttpResponse(json.dumps(rep.__dict__))


def login(request):
    rep = BaseResponse()
    print(request.POST)
    form = LoginFrom(request.POST)
    if form.is_valid():
        value_dict = form.clean()
        # 验证码
        print('生产的验证码', request.session["CheckCode"].lower())
        print('生产的验证码', value_dict['code'].lower())
        if value_dict['code'].lower() != request.session["CheckCode"].lower():
            rep.message = {'code': [{'message': '验证码错误'}]}
            return HttpResponse(json.dumps(rep.__dict__))
        from django.db.models import Q
        # 用户名|邮箱 与密码是否匹配
        obj = models.UserInfo.objects.filter(
            Q(Q(email=value_dict['user']) & Q(password=value_dict['pwd'])) | Q(
                Q(username=value_dict['user']) & Q(password=value_dict['pwd']))
        ).first()
        if not obj:
            rep.message = {'user': [{'message': '用户名或密码错误'}]}
            return HttpResponse(json.dumps(rep.__dict__))
        rep.status = True
        request.session['is_login'] = True
        request.session['user_info'] = {'nid': obj.nid, 'email': obj.email,
                                        'username': obj.username}

    else:
        err_msg = form.errors.as_json()
        rep.message = json.loads(err_msg)
    print('返回前端： ', rep.message)
    return HttpResponse(json.dumps(rep.__dict__))


def login_out(request):
    request.session.clear()
    return redirect('/index.html/')
