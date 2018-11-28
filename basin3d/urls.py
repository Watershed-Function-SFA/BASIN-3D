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
from basin3d.models import DataSource
from basin3d.synthesis.viewsets import RegionViewSet, \
    DataPointGroupViewSet, DataPointViewSet, SiteViewSet, PlotViewSet, \
    PointLocationViewSet
from basin3d.views import broker_api_root
from basin3d.viewsets import DataSourceViewSet, DirectAPIViewSet, MeasurementVariableViewSet, \
    MeasurementViewSet
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers


def get_synthesis_router():
    """
    Generate the router for the Synthesis API.

    :return: Synthesis Router
    :rtype: :class:`routers.DefaultRouter`
    """
    router = routers.DefaultRouter()
    if settings.BASIN3D["SYNTHESIS"]:

        router.register(r'datasources', DataSourceViewSet, base_name='datasource')
        router.register(r'variables', MeasurementVariableViewSet, base_name='measurementvariable')
        router.register(r'measurements', MeasurementViewSet, base_name='measurement')
        try:
            # iterate over the Datasources and register ViewSets to the router
            # for those models that are defined.
            for datasource in DataSource.objects.all():
                viewset_models = []
                plugin = datasource.get_plugin()  # Get the plugin model

                if datasource.enabled:

                    plugin_views = plugin.get_plugin_views()
                    for model_name in plugin_views.keys():
                        viewset_models.append(model_name.__name__)

                    # This is OK for now in the future we want this to be more automated
                    # This will only add the viewsets that are defined
                    viewset_models = set(viewset_models)
                    if 'Region' in viewset_models:
                        router.register(r'regions', RegionViewSet, base_name='region')
                    if 'Site' in viewset_models:
                        router.register(r'sites', SiteViewSet, base_name='site')
                    if 'Plot' in viewset_models:
                        router.register(r'plots', PlotViewSet, base_name='plot')
                    if 'PointLocation' in viewset_models:
                        router.register(r'point_locations', PointLocationViewSet,
                                        base_name='pointlocation')
                    if 'DataPointGroup' in viewset_models:
                        router.register(r'data_point_groups', DataPointGroupViewSet,
                                        base_name='datapointgroup')
                    if 'DataPoint' in viewset_models:
                        router.register(r'data_points', DataPointViewSet, base_name='datapoint')
        except Exception:
            # This will only be raised during a migration because the database has not been
            # created yet.
            pass

    return router

# Wire up our API using automatic URL routing.


# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', broker_api_root, name='broker-api-root' )
]

router = get_synthesis_router()
if settings.BASIN3D["SYNTHESIS"]:
    urlpatterns.append(url(r'^synthesis/', include(router.urls)))

if settings.BASIN3D["DIRECT_API"]:
    urlpatterns.append(url(r'^direct/$',DirectAPIViewSet.as_view({'get':'list'}),name='direct-api-list'))
    urlpatterns.append(url(r'^direct/(?P<id_prefix>[a-zA-Z0-9]+)/(?P<direct_path>[a-zA-Z/_\-?&0-9]*)$',
        DirectAPIViewSet.as_view({'get': 'retrieve', 'post':'retrieve'}),
        name='direct-path-detail'))