from cryptography.exceptions import InvalidSignature
from django.contrib.auth import get_user_model
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication, AuthenticationFailed

from basiclive.utils.signing import Signer


def get_v2_user(request):
    url_data = resolve(request.path)
    kwargs = url_data.kwargs
    if 'username' in kwargs and 'signature' in kwargs:
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=kwargs.get('username'))
        except user_model.DoesNotExist:
            return None
        else:
            if not user.key:
                return None

        try:
            signer = Signer(public=user.key)
            value = signer.unsign(kwargs.get('signature'))
        except InvalidSignature:
            return None
        else:
            if value != kwargs.get('username'):
                return None
        return user


def get_v3_user(request):
    authenticator = JWTAuthentication()
    try:
        user_data = authenticator.authenticate(request)
    except AuthenticationFailed:
        user_data = None
    if user_data:
        return user_data[0]


class APIAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = None
        if request.path.startswith('/api/v2'):
            user = get_v2_user(request)
        elif request.path.startswith('/api/v3'):
            user = get_v3_user(request)

        if user:
            request.user = user
