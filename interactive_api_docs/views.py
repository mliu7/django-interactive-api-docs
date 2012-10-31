from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import TemplateView


def interactive_api_docs_home(request):
    from interactive_api_docs.spec import full_spec #Import here to avoid a circular dependency due 
                                                    #to full_spec calling reverse()
    domain = Site.objects.get_current().domain
    protocol = request.META['wsgi.url_scheme']
    access_token = ''

    # Get an access token for the registered user if the user is logged in
    callback_string = settings.IAD_ACCESS_TOKEN_CALLBACK
    if callback_string:
        split_callback_string = callback_string.split('.')
        method_name = split_callback_string.pop(-1)
        module_name = ''.join(split_callback_string)

        # Import the module
        callback_module = __import__(module_name)
        callback_method = getattr(callback_module, method_name)
        access_token = callback_method(request)

    context = {'spec': full_spec,
               'api_base_uri': settings.IAD_BASE_API_URL,
               'access_token': access_token}
    return render(request, 'interactive_api_docs_home.html', context)
