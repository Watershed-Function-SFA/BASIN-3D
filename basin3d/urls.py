"""wfsfa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

admin.autodiscover()

from basin3d.synthesis.viewsets import SearchViewSet, SitesViewSet, LocationsViewSet

router = routers.DefaultRouter()
router.register(r'sites', SitesViewSet, base_name='site')
router.register(r'locations', LocationsViewSet, base_name='location')
router.register(r'search', SearchViewSet, base_name='search')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^v1/', include(router.urls, namespace='v1')),
    url(r'^admin/', include(admin.site.urls)),  # admin site
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
