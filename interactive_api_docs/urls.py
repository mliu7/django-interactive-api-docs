from __future__ import unicode_literals

from django.conf.urls.defaults import *
from django.views.generic import TemplateView


from interactive_api_docs.views import interactive_api_docs_home

urlpatterns = patterns(
    '',
    url(r'^$', 'interactive_api_docs.views.interactive_api_docs_home', name='interactive_api_docs_home'),
)
