from cryptography.exceptions import InvalidSignature
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import resolve, Resolver404
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication, AuthenticationFailed

from basiclive.core.lims.models import Project
from basiclive.utils.signing import Signer


def get_v2_user(request):
    try:
        url_data = resolve(request.path)
        kwargs = url_data.kwargs
    except Resolver404:
        return None
    except Exception:
        return None

    if 'username' in kwargs and 'signature' in kwargs:
        username = kwargs.get('username')
        signature = kwargs.get('signature')
        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()
        project = Project.objects.filter(Q(username__exact=username) | Q(name__exact=username)).first()

        public_key = None
        if user and getattr(user, 'key', None):
            public_key = user.key
        elif project and project.key:
            public_key = project.key

        if not public_key:
            return None

        try:
            signer = Signer(public=public_key)
            value = signer.unsign(signature)
        except InvalidSignature:
            return None
        else:
            if value != username:
                return None

        if project:
            request.project = project

        if user:
            return user
        elif project and project.pi:
            return project.pi

    return None


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
        if request.path.startswith('/api/'):
            # Try JWT first (V3)
            user = get_v3_user(request)
            if not user:
                # Fallback to V2 URL signature
                user = get_v2_user(request)
        elif request.path.startswith('/api/v2'):
            user = get_v2_user(request)
            if not user:
                user = get_v3_user(request)
        elif request.path.startswith('/api/v3'):
            user = get_v3_user(request)

        if user:
            request.user = user
