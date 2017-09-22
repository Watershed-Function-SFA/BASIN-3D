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
from django.conf import settings
from django.core.urlresolvers import NoReverseMatch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


BASIN3D_DIRECT_VIEWS = [('direct-apis', 'direct-api-list')]\

BASIN3D_SYNTHESIS_VIEWS = [('synthesis-datasources', 'datasource-list'),
                           ('synthesis-variables', 'measurementvariable-list'),
                           ('synthesis-measurements', 'measurement-list'),
                           ('synthesis-regions', 'region-list'),
                           ('synthesis-sites', 'site-list'),
                           ('synthesis-plots', 'plot-list'),
                           ('synthesis-pointlocations', 'pointlocation-list'),
                           ('synthesis-datapointgroups', 'datapointgroup-list'),
                           ('synthesis-datapoints', 'datapoint-list'),
                           ]


@api_view(['GET'])
def broker_api_root(request, format=None):
    """
    """
    root_dict = OrderedDict()
    # Iterate over the possible views. If they are enabled add them to the
    # root api.
    views =[]
    if settings.BASIN3D["SYNTHESIS"]:
        views.extend(BASIN3D_SYNTHESIS_VIEWS)
    if settings.BASIN3D["DIRECT_API"]:
        views.extend(BASIN3D_DIRECT_VIEWS)
    for k, v in views:

        try:
            root_dict[k] = reverse(v, request=request, format=format)
        except NoReverseMatch:
            # If there is no match just don't show it
            pass

    return Response(root_dict)
