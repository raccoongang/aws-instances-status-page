from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views


app_name = 'ec2'

urlpatterns = [
    url(r'^$', views.Homepage.as_view(), name='index'),
    url(r'^login_error/$', views.LoginError.as_view(), name='login_error'),
    url(r'^after_login_redirect/$', login_required(views.AfterLoginRedirect.as_view()), name='after_login_redirect'),
    url(r'^(?P<instance>[-\w\+%_&]+)/$', login_required(views.Instance.as_view()), name='instance')
]
