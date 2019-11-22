import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .tools import BaseResponse


class GlobalException(MiddlewareMixin):

    def process_exception(self, _, exception):
        rep = BaseResponse()
        rep.error = str(exception)
        rep.code = 500
        return JsonResponse(rep.__dict__)
