from allauth import urls

urls.urlpatterns.pop(0)
urlpatterns = urls.urlpatterns
