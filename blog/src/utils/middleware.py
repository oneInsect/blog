import json
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class GlobalException(MiddlewareMixin):

    def process_exception(self, _, exception):
        return HttpResponse(content=json.dumps({"msg": str(exception)}),
                            status=500)
