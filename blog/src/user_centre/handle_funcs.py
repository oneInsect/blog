

import json
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from django.shortcuts import redirect
from django.http import JsonResponse
from django import forms

from user_centre import models
from utils import (get_logger, get_hash_code, BaseResponse, parse_ini)


LOG = get_logger("user_centre")


def login(request):
    rep = BaseResponse()
    form = LoginFrom(request.POST)
    if form.is_valid():
        value_dict = form.clean()
        value_dict['pwd'] = get_hash_code(value_dict['pwd'])
        if value_dict['code'].lower() != request.session["CheckCode"].lower():
            fail_reason = 'verification code error'
            rep.message = {'code': [{'message': fail_reason}]}
            LOG.info("%s attempt login, result=fail, reason=%s".format(
                value_dict['username'], fail_reason))
            return JsonResponse(rep.__dict__)
        from django.db.models import Q
        obj = models.UserInfo.objects.filter(
            Q(Q(email=value_dict['username']) & Q(password=value_dict['pwd'])) | Q(
                Q(username=value_dict['username']) & Q(password=value_dict['pwd']))
        ).first()
        if not obj:
            fail_reason = 'username or password wrong'
            rep.message = {'username': [{'message': fail_reason}]}
            LOG.info("%s attempt login, result=fail, reason=%s".format(
                value_dict['username'], fail_reason))
            return JsonResponse(rep.__dict__)
        request.session['is_login'] = True
        request.session.update({'nid': obj.nid, 'email': obj.email,
                                'username': obj.username})
        LOG.info("%s attempt login, result=success".format(value_dict['username']))
    else:
        err_msg = form.errors.as_json()
        rep.message = json.loads(err_msg)
        LOG.info("%s attempt login, result=fail, reason=%s".format(
            request.POST.get('username'), rep.message))
    return JsonResponse(rep.__dict__)


def logout(request):
    request.session.clear()
    return redirect('/')


class SendMsgForm(forms.Form):
    email = forms.EmailField()


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32, min_length=6,
                               error_messages={
                                   'min_length': 'Requires at least 6 bytes',
                                   'max_length': 'No more than 32 bytes',
                                   'required': "username can't be empty"})
    email = forms.EmailField(max_length=32,
                             error_messages={'invalid': 'email invalid',
                                             'max_length': 'No more than 32 bytes',
                                             'required': "email can't be empty"})
    email_code = forms.CharField(max_length=6,
                                 error_messages={
                                     'required': "verify code can't be empty",
                                     'max_length': 'No more than 6 bytes'})
    password = forms.CharField(max_length=32, min_length=6,
                               error_messages={
                                   'min_length': 'Requires at least 6 bytes',
                                   'max_length': 'No more than 32 bytes',
                                   'required': "password can't be empty"})


class LoginFrom(forms.Form):
    username = forms.CharField(max_length=32, min_length=6,
                           error_messages={
                               'min_length': 'Requires at least 6 bytes',
                               'max_length': 'No more than 32 bytes',
                               'required': "username or email can't be empty"})
    pwd = forms.CharField(max_length=32, min_length=6,
                          error_messages={
                              'min_length': 'Requires at least 6 bytes',
                              'max_length': 'No more than 32 bytes',
                              'required': "password can't be empty"})
    code = forms.CharField(error_messages={'required': "verify code can't be empty"})


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


def send_code(code, receiver):
    _user = parse_ini("blog.ini", "email", "username")
    _pwd = parse_ini("blog.ini", "email", "password")
    _email_host = parse_ini("blog.ini", "email", "host")
    _email_port = int(parse_ini("blog.ini", "email", "port"))
    text = "<h1>Register Verification Code</h1><p>" \
           "Your verification code is %s, " \
           "please enter this code to your blog register page, " \
           "this code will expire after 60 seconds</p>" % code
    msg = MIMEText(text, 'html')
    msg["Subject"] = "Verification code"
    msg["From"] = _user
    msg["To"] = receiver
    try:
        server = smtplib.SMTP_SSL(host=_email_host, port=_email_port)
        server.login(user=_user, password=_pwd)
        server.sendmail(from_addr=_user, to_addrs=receiver,
                        msg=msg.as_string())
        server.quit()
        LOG.info("Send email to %s success!" % receiver)
    except smtplib.SMTPException as email_error:
        LOG.error("Send email to %s error!, reason=%s" % (receiver, email_error))


def send_email_verify_code(request):
    rep = BaseResponse()
    form = SendMsgForm(request.GET)
    if form.is_valid():
        value_dict = form.clean()
        email = value_dict['email']
        has_email_exist = models.UserInfo.objects.filter(email=email).count()
        if has_email_exist:
            rep.error = 'This email address has already registered'
            return JsonResponse(rep.__dict__)
        current_date = datetime.datetime.now()
        code = random_code()
        count = models.SendMsg.objects.filter(email=email).count()
        if not count:
            models.SendMsg.objects.create(email=email, email_code=code,
                                          ctime=current_date)
        else:
            limit_time = current_date - datetime.timedelta(hours=1)
            times = models.SendMsg.objects.filter(email=email,
                                                  ctime__gt=limit_time,
                                                  times__gt=9).count()
            if times:
                rep.error = 'please try again after one hour!'
            else:
                unfreeze = models.SendMsg.objects.filter(email=email,
                                                         ctime__lt=limit_time).count()
                if unfreeze:
                    models.SendMsg.objects.filter(email=email).update(times=0)
                from django.db.models import F
                models.SendMsg.objects.filter(email=email).update(
                    email_code=code, ctime=current_date, times=F("times") + 1)
                rep.status = True
        send_code(code, email)
    else:
        rep.error = form.errors['email'][0]
    return JsonResponse(rep.__dict__)


def register_backend(request):
    rep = BaseResponse()
    form = RegisterForm(request.POST)
    if form.is_valid():
        value_dict = form.clean()
        current_time = datetime.datetime.now()
        limit_time = current_time - datetime.timedelta(minutes=1)
        timeout = models.SendMsg.objects.filter(email=value_dict['email'],
                                                email_code=value_dict[
                                                    'email_code'],
                                                ctime__lt=limit_time).count()
        if timeout:
            rep.error = 'verification code error or expired'
            rep.code = 422
            LOG.error("%s was register failed, reason=%s" % (value_dict['email'],
                                                             rep.error))
            return JsonResponse(rep.__dict__)
        has_username_exist = models.UserInfo.objects.filter(
            username=value_dict['username']).count()
        if has_username_exist:
            rep.code = 422
            rep.message['username'] = 'username has already exist'
            LOG.error("%s was register failed, reason=%s" % (value_dict['email'],
                                                             rep.error))
            return JsonResponse(rep.__dict__)
        has_email_exist = models.UserInfo.objects.filter(
            email=value_dict['email']).count()
        if has_email_exist:
            rep.code = 422
            rep.message['email'] = 'email has already exist'
            LOG.error("%s was register failed, reason=%s" % (value_dict['email'],
                                                             rep.error))
            return JsonResponse(rep.__dict__)
        value_dict.pop('email_code')
        value_dict['ctime'] = current_time
        value_dict["password"] = get_hash_code(value_dict["password"])
        obj = models.UserInfo.objects.create(**value_dict)
        models.SendMsg.objects.filter(email=value_dict['email']).delete()
        rep.code = 201
        request.session['is_login'] = True
        request.session.update({'nid': obj.nid, 'email': obj.email,
                                'username': obj.username})
        LOG.info("%s was register success" % obj.email)
    else:
        err_msg = form.errors.as_json()
        rep.error = json.loads(err_msg)
        rep.status = 500
        LOG.error("%s was register failed, reason=%s" % (request.POST.get('email'),
                                                         rep.error))
    return JsonResponse(rep.__dict__)