from __future__ import absolute_import, unicode_literals
from django.conf.urls import patterns, url
from widgets.views import WidgetBuilderView, WidgetView


urlpatterns = patterns('',
    url(r'^$', WidgetBuilderView.as_view(), name='widgets-select'),
    url(r'^(?P<widget>[_\w]+)/$', WidgetView.as_view(), name='widgets-detail'),
    url(r'^(?P<widget>[_\w]+)/build/$', WidgetBuilderView.as_view(), name='widgets-build'),
)
