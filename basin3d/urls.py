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
import string

from basin3d.models import DataSource, get_feature_types
from basin3d.synthesis.viewsets import MonitoringFeatureViewSet, \
    MeasurementTimeseriesTVPObservationViewSet
from basin3d.views import broker_api_root, monitoring_features_lists
from basin3d.viewsets import DataSourceViewSet, DirectAPIViewSet, \
    ObservedPropertyViewSet, ObservedPropertyVariableViewSet
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
        router.register(r'observedpropertyvariables', ObservedPropertyVariableViewSet, base_name='observedpropertyvariable')
        router.register(r'observedproperty', ObservedPropertyViewSet, base_name='observedproperty')
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
                    if 'MeasurementTimeseriesTVPObservation' in viewset_models:
                        router.register(r'measurement_tvp_timeseries', MeasurementTimeseriesTVPObservationViewSet,
                                        base_name='measurementtvptimeseries')
        except Exception:
            # This will only be raised during a migration because the database has not been
            # created yet.
            pass

    return router


def get_monitoring_feature_urls():
    """

    :return: list of url objects
    """
    urls = []
    try:
        # iterate over the Datasources and register ViewSets to the router
        # for those models that are defined.
        supported_feature_types = get_feature_types()
        for datasource in DataSource.objects.all():
            viewset_models = []
            plugin = datasource.get_plugin()  # Get the plugin model

            if datasource.enabled:

                plugin_views = plugin.get_plugin_views()
                for model_name in plugin_views.keys():
                    viewset_models.append(model_name.__name__)

                datasource_feature_types = plugin.get_feature_types()
                for feature_type in datasource_feature_types:
                    if feature_type in supported_feature_types:
                        ft = ''.join(feature_type.lower().split())
                        path_route = '^synthesis/monitoringfeatures/{}s'.format(ft)
                        urls.extend([
                            url(r'{}/$'.format(path_route),
                                MonitoringFeatureViewSet.as_view({'get': 'list'}),
                                name='monitoringfeature-list'),
                            url(r'{}\.(?P<format>[a-z0-9]+)/?$'.format(path_route),
                                MonitoringFeatureViewSet.as_view({'get': 'list'}),
                                name='monitoringfeature-list'),
                            url(r'{}/(?P<pk>[^/.]+)/$'.format(path_route),
                                MonitoringFeatureViewSet.as_view({'get': '{}s'.format(ft)}),
                                name='monitoringfeature-{}s-detail'.format(ft)),
                            url(r'{}/(?P<pk>[^/.]+).(?P<format>[a-z0-9]+)/?'.format(path_route),
                                MonitoringFeatureViewSet.as_view({'get': '{}s'.format(ft)}),
                                name='monitoringfeature-{}s-detail'.format(ft))
                        ])
                        supported_feature_types.remove(feature_type)

        return urls
    except Exception:
        pass

# Wire up our API using automatic URL routing.

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', broker_api_root, name='broker-api-root'),
    url(r'^synthesis/monitoringfeatures/$', monitoring_features_lists, name='monitoring-features-list')
]

urlpatterns.extend(get_monitoring_feature_urls())

router = get_synthesis_router()
if settings.BASIN3D["SYNTHESIS"]:
    urlpatterns.append(url(r'^synthesis/', include(router.urls)))

if settings.BASIN3D["DIRECT_API"]:
    urlpatterns.append(url(r'^direct/$', DirectAPIViewSet.as_view({'get':'list'}), name='direct-api-list'))
    urlpatterns.append(url(r'^direct/(?P<id_prefix>[a-zA-Z0-9]+)/(?P<direct_path>[a-zA-Z/_\-?&0-9]*)$',
                           DirectAPIViewSet.as_view({'get': 'retrieve', 'post':'retrieve'}),
                           name='direct-path-detail'))
