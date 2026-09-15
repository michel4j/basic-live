from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from basiclive.core.lims.conf import settings as lims_settings
from . import views


urlpatterns = [
    path('auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('data/<slug:beamline>/', views.AddData.as_view()),
    path('report/<slug:beamline>/', views.AddReport.as_view()),
    path('samples/<slug:beamline>/', views.ProjectSamples.as_view()),
    path('session/<slug:beamline>/<slug:session>/start/', views.LaunchSession.as_view()),
    path('session/<slug:beamline>/<slug:session>/close/', views.CloseSession.as_view()),

]

if lims_settings.USE_ACL:
    import basiclive.core.acl.views as acl_views
    urlpatterns += [
        path('accesslist/', acl_views.EndpointList.as_view()),
        path('keys/<slug:username>', acl_views.AccessKeys.as_view()),
    ]
