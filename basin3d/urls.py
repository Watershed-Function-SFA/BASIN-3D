"""basin3d URL Configuration

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
import djangoplugins
from basin3d.models import DataSource
from basin3d.synthesis.viewsets import RegionsViewSet, ModelViewSet, ModelDomainViewSet
from django.conf.urls import url, include
from django.db import OperationalError
from rest_framework import routers

router = routers.DefaultRouter()


try:
    viewset_models = []
    # iterate over the Datasources and register ViewSets to the router
    # for those models that are defined.
    for datasource in DataSource.objects.all():
        plugin_model = datasource.plugin  # Get the plugin model

        if plugin_model.status == djangoplugins.models.ENABLED:

            plugin_views = plugin_model.get_plugin().get_plugin_views()
            for model_name in plugin_views.keys():
                viewset_models.append(model_name.__name__)

            # This is OK for now in the future we want this to be more automated
            # This will only add the viewsets that are define
            viewset_models = set(viewset_models)
            if 'Region' in viewset_models:
                router.register(r'regions', RegionsViewSet, base_name='region')
            if 'Model' in viewset_models:
                router.register(r'models', ModelViewSet, base_name='model')
            if 'ModelDomain' in viewset_models:
                router.register(r'model_domains', ModelDomainViewSet, base_name='modeldomain')
except OperationalError as e:
    # This will only be raised during a migration because the database has not been
    # created yet.
    pass

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^v1/', include(router.urls, namespace='v1')),
]
