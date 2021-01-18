import re

from django.http import HttpResponse
from django.shortcuts import redirect


def view_404(request, exception):
    # make a redirect to homepage
    # you can use the name of url or just the plain link
    return redirect('/')  # or redirect('name-of-index-url')


def view_google_site_verification(request):
    path = ''
    if request.path:
        path = re.sub("[^A-Za-z0-9.]", "", request.path)
    return HttpResponse("google-site-verification: %s" % path)
