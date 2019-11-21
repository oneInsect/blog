

import json
import random
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
        rep.status = True
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
    _to = receiver
    msg = MIMEText(code)
    msg["Subject"] = "Verification code"
    msg["From"] = 'lance@blog.com'
    msg["To"] = _to

    # try:
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    print(_user, _pwd)
    s.login(_user, _pwd)
    s.sendmail(_user, _to, msg.as_string())
    s.quit()
    LOG.info("Success!")
    # except smtplib.SMTPException as email_error:
    #     LOG.info("Error: %s" % email_error)

