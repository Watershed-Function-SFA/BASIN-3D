"""
`basin3d.views`
***************

.. currentmodule:: basin3d.views

:platform: Unix, Mac
:synopsis: BASIN-3D Views
:module author: Val Hendrix <vhendrix@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top
"""
from collections import OrderedDict
import logging
import sys

from basin3d.models import DataSource, FeatureTypes, get_feature_types
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse, NoReverseMatch


logger = logging.getLogger(__name__)

BASIN3D_DIRECT_VIEWS = [('direct-apis', 'direct-api-list')]\

BASIN3D_SYNTHESIS_VIEWS = [('synthesis-datasources', 'datasource-list'),
                           ('synthesis-observedpropertyvariables', 'observedpropertyvariable-list'),
                           ('synthesis-observedproperty', 'observedproperty-list'),
                           ('synthesis-measurementtvptimeseries', 'measurementtvptimeseries-list'),
                           ]


@api_view(['GET'])
def broker_api_root(request, format=None):
    """
    """
    root_dict = OrderedDict()
    # Iterate over the possible views. If they are enabled add them to the
    # root api.
    views = []
    if settings.BASIN3D["SYNTHESIS"]:
        views.extend(BASIN3D_SYNTHESIS_VIEWS)
    if settings.BASIN3D["DIRECT_API"]:
        views.extend(BASIN3D_DIRECT_VIEWS)
    for k, v in views:
        try:
            root_dict[k] = reverse(v, request=request, format=format)
        except NoReverseMatch:
            # If there is no match just don't show it
            print("NoReversMatch for {}".format(k), file=sys.stderr)
    root_dict['synthesis-monitoringfeatures'] = \
        '{}://{}/synthesis/monitoringfeatures/'.format(request.scheme, request.META["HTTP_HOST"])
    return Response(root_dict)


@api_view(['GET'])
def monitoring_features_lists(request, format=format):
    """
    Generate list of URLs to views for monitoring features based on availability in datasource
    """
    monitoring_features_list = {}
    supported_feature_types = get_feature_types()
    for datasource in DataSource.objects.all():
        viewset_models = []
        plugin = datasource.get_plugin()  # Get the plugin model

        if datasource.enabled:

            plugin_views = plugin.get_plugin_views()
            for model_name in plugin_views.keys():
                viewset_models.append(model_name.__name__)

            datasource_feature_types = plugin.get_feature_types()
            unsupported_feature_types = []
            for feature_type in datasource_feature_types:
                if feature_type in supported_feature_types:
                    ft = ''.join(feature_type.lower().split())
                    monitoring_features_list['{}s'.format(ft)] = \
                        '{}://{}/synthesis/monitoringfeatures/{}s/'.format(
                            request.scheme, request.META["HTTP_HOST"], ft)
                    supported_feature_types.remove(feature_type)
                elif feature_type not in unsupported_feature_types:
                    unsupported_feature_types.append(feature_type)

            if len(unsupported_feature_types) > 0:
                logger.warning("{} are not supported FeatureTypes in {}.".format(", ".join(unsupported_feature_types), datasource.name))

    return Response(monitoring_features_list)
