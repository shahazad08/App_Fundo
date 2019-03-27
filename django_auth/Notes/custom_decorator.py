from django.http import JsonResponse, HttpResponse
from users import models
from users.models import User
from users.services import redis_information
import jwt
from self import self

def custom_login(function):
    def wrap(request, *args, **kwargs):
        res = {}
        try:
            token = redis_information.get_token(self, 'token')  # Redis Cache GET
            token_decode = jwt.decode(token, "secret_key", algorithms=['HS256'])
            eid = token_decode.get('email')  # Additional code of a decorator to get an email
            user_id = User.object.get(email=eid)
            # return user.id
            print("Tokensss",token)
            entry=user_id
            print("User",entry)
            request.user_id = user_id
            if entry:
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        except Exception as e:
            print(e)
            res['message'] = 'Something bad happend'
            return JsonResponse(res, status=404)
            # return function(request, *args, **kwargs)
    return wrap

