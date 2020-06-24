"""django_basin3d URL Configuration

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

from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from django_basin3d.models import DataSource, get_feature_types
from django_basin3d.synthesis.viewsets import MeasurementTimeseriesTVPObservationViewSet, MonitoringFeatureViewSet
from django_basin3d.views import broker_api_root, monitoring_features_lists
from django_basin3d.viewsets import DataSourceViewSet, ObservedPropertyVariableViewSet, ObservedPropertyViewSet


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

            plugin_views = plugin.get_plugin_access()
            for model_name in plugin_views.keys():
                viewset_models.append(model_name.__name__)

            datasource_feature_types = plugin.get_feature_types()
            for feature_type in datasource_feature_types:
                if feature_type in supported_feature_types:
                    ft = ''.join(feature_type.lower().split())
                    path_route = '^monitoringfeatures/{}s'.format(ft)
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

    except Exception as e:
        print(e)
    return urls


# Wire up our API using automatic URL routing.
router = routers.DefaultRouter()
router.register(r'datasources', DataSourceViewSet, basename='datasource')
router.register(r'observedpropertyvariables', ObservedPropertyVariableViewSet,
                basename='observedpropertyvariable')
router.register(r'observedproperty', ObservedPropertyViewSet, basename='observedproperty')

# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Broker Root Path View
    url(r'^$', broker_api_root, name='broker-api-root'),

    # Views to Dynamic Views
    url(r'^measurement_tvp_timeseries/$', MeasurementTimeseriesTVPObservationViewSet.as_view({"get": "list"}),
        name='monitoring-features-list'),
    url(r'^monitoringfeatures/$', monitoring_features_lists, name='monitoring-features-list'),
]

urlpatterns.extend(get_monitoring_feature_urls())
urlpatterns.append(url(r'^', include(router.urls)))
