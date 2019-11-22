
import io
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from utils import BaseResponse, login_required, create_validate_code

from .handle_funcs import (login, logout, send_email_verify_code,
                           register_backend)


@require_http_methods(['GET'])
def send_email(request):
    return send_email_verify_code(request)

@require_http_methods(['POST'])
def register(request):
    return register_backend(request)


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
    img, code = create_validate_code()
    img.save(stream, "PNG")
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())