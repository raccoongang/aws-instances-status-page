from django.conf.urls import url
from . import views

app_name = 'ec2'

urlpatterns = [
    url(r'^$', views.Homepage.as_view(), name='index'),
    url(r'^(?P<user>\w+)/(?P<instance>[-\w\+%_&]+)/$', views.Instance.as_view(), name='instance'),
]
