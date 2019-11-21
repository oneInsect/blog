
import io
import json
import datetime
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from user_centre import models
from utils import BaseResponse, login_required, create_validate_code

from .handle_funcs import (SendMsgForm, random_code, login, logout, send_code,
                           RegisterForm)


@require_http_methods(['GET'])
def send_email(request):
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
            rep.status = True
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


def register(request):
    rep = BaseResponse()
    form = RegisterForm(request.POST)
    if form.is_valid():
        value_dict = form.clean()
        print(value_dict)
        current_time = datetime.datetime.now()
        limit_time = current_time - datetime.timedelta(minutes=1)

        timeout = models.SendMsg.objects.filter(email=value_dict['email'],
                                                email_code=value_dict[
                                                    'email_code'],
                                                ctime__lt=limit_time).count()
        if timeout:
            rep.message['email_code'] = 'verification code error or expired'
            return JsonResponse(rep.__dict__)
        has_username_exist = models.UserInfo.objects.filter(
            username=value_dict['username']).count()
        if has_username_exist:
            rep.message['username'] = 'username has already exist'
            return JsonResponse(rep.__dict__)
        has_email_exist = models.UserInfo.objects.filter(
            email=value_dict['email']).count()
        if has_email_exist:
            rep.message['email'] = 'email has already exist'
            return JsonResponse(rep.__dict__)
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
    return JsonResponse(rep.__dict__)


@require_http_methods(['POST', 'GET'])
def session_manage(request):
    if request.method == "POST":
        return login(request)
    elif request.method == "GET":
        return logout(request)
    else:
        return Http404()


@require_http_methods(['GET'])
@login_required
def get_user_info(request):
    rep = BaseResponse()
    rep.message["username"] = request.session.get("username") or request.session.get("email")
    return JsonResponse(rep.__dict__)


@require_http_methods(['GET'])
def check_code(request):
    """
    获取验证码
    :param request:
    :return:
    """
    stream = io.BytesIO()
    # 创建随机字符 code
    # 创建一张图片格式的字符串，将随机字符串写到图片上
    img, code = create_validate_code()
    img.save(stream, "PNG")
    # 将字符串形式的验证码放在Session中
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())