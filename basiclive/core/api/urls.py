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

    # V3 routes (JWT Bearer Token / request.project context)
    path('data/<slug:beamline>/', views.AddData.as_view(), name='api-data'),
    path('report/<slug:beamline>/', views.AddReport.as_view(), name='api-report'),
    path('samples/<slug:beamline>/', views.ProjectSamples.as_view(), name='api-project-samples'),
    path('session/<slug:beamline>/<slug:session>/start/', views.LaunchSession.as_view(), name='api-session-start'),
    path('session/<slug:beamline>/<slug:session>/close/', views.CloseSession.as_view(), name='api-session-close'),
    path('project/', views.UpdateUserKey.as_view(), name='api-project-key'),

    # V2 legacy routes (asymmetric signed URL fallback)
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/data/(?P<beamline>[\w_-]+)/$', views.AddData.as_view(), name='v2-data'),
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/report/(?P<beamline>[\w_-]+)/$', views.AddReport.as_view(), name='v2-report'),
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/samples/(?P<beamline>[\w_-]+)/$', views.ProjectSamples.as_view(), name='v2-project-samples'),
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/launch/(?P<beamline>[\w_-]+)/(?P<session>[\w_-]+)/$', views.LaunchSession.as_view(), name='v2-session-launch'),
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/close/(?P<beamline>[\w_-]+)/(?P<session>[\w_-]+)/$', views.CloseSession.as_view(), name='v2-session-close'),
    re_path(r'^(?P<signature>(?P<username>[\w_-]+):.+)/project/$', views.UpdateUserKey.as_view(), name='v2-project-update'),
]

if lims_settings.USE_ACL:
    import basiclive.core.acl.views as acl_views
    urlpatterns += [
        path('accesslist/', acl_views.EndpointList.as_view()),
        path('keys/<slug:username>', acl_views.AccessKeys.as_view()),
    ]
