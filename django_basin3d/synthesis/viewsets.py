"""
`django_basin3d.synthesis.viewsets`
****************************

.. currentmodule:: django_basin3d.synthesis.viewsets

:synopsis: BASIN-3D Synthesis Model Viewsets (View Controllers) that support the REST API
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>


Below is the inheritance diagram for BASIN-3D Viewsets.  All of the views are based on
:class:`DataSourcePluginViewSet` which provide all the synthesis logic for viewing data
from the connected data sources.

.. inheritance-diagram:: django_basin3d.synthesis.viewsets
    :top-classes: django_basin3d.synthesis.viewsets.DataSourcePluginViewSet
    :parts: 2

----------------------------------

"""
import logging

import typing
from rest_framework import status, versioning
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from basin3d.core.models import MeasurementTimeseriesTVPObservation, MonitoringFeature
from basin3d.core.synthesis import DataSourceModelAccess, MeasurementTimeseriesTVPObservationAccess, \
    MonitoringFeatureAccess

from basin3d.core.types import FeatureTypes
from django_basin3d.models import DataSource
from django_basin3d.synthesis.serializers import MeasurementTimeseriesTVPObservationSerializer, \
    MonitoringFeatureSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_request_feature_type(request, return_format="enum"):
    """
    Return the feature type if exists in the request
    :param request: request
    :param return_format: "enum" (default) = the FeatureTypes enum,
                   otherwise return the text version
    :return: the feature_type in the format specified, None if none exists
    """
    path_info = request.path_info.split("/")
    for k, feature_type in FeatureTypes.TYPES.items():
        ft = "{}s".format("".join(feature_type.lower().split()))
        if ft in path_info:
            if return_format == "enum":
                return FeatureTypes.TYPES[k].lower()
            else:
                return feature_type
    return None


class DataSourcePluginViewSet(ViewSet, DataSourceModelAccess):
    """
    Base ViewsSet for all DataSource plugins.  The inheritance diagram shows that this class extends the
    `Django Rest Framework <https://www.django-rest-framework.org/>`_
    class :class:`rest_framework.viewsets.ViewSet`. These are based on `Django generic views
    <https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/>`_.

    .. inheritance-diagram:: rest_framework.viewsets.ViewSet django_basin3d.synthesis.viewsets.DataSourcePluginViewSet

    """
    versioning_class = versioning.NamespaceVersioning

    def __init__(self):
        # Override super class
        from django_basin3d.catalog import CatalogDjango
        self._catalog = CatalogDjango()

    @property
    def plugins(self):
        plugins = {}
        for d in DataSource.objects.all():
            plugins[d.id_prefix] = d.get_plugin()
        return plugins

    @property
    def catalog(self):
        return self._catalog

    def list(self, **kwargs) -> Response:
        """
        Return the synthesized plugin results

        :param request: The incoming request object
        :type request: :class:`rest_framework.request.Request`
        :param format: The format to present the data (default is json)
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """
        items = []

        if "request" not in kwargs:
            raise Response({"success": False, "detail": "Request is missing"}, status=status.HTTP_400_BAD_REQUEST)

        request = kwargs['request']
        feature_type = get_request_feature_type(request)

        params = request.query_params.dict()
        for i in super(DataSourcePluginViewSet, self).list(feature_type=feature_type, **params):
            items.append(i)

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, pk: str, **kwargs) -> Response:
        """
        Retrieve a single synthesized value

        :param request: The request object
        :type request: :class:`rest_framework.request.Request`
        :param pk: The primary key
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """

        # split the datasource id prefix from the primary key
        if "request" not in kwargs:
            return Response({'success': False, 'detail': "Request is missing"},
                            status=status.HTTP_400_BAD_REQUEST, )

        request = kwargs['request']
        feature_type = get_request_feature_type(request)

        try:
            item = super(DataSourcePluginViewSet, self).retrieve(pk=pk, feature_type=feature_type, **request.query_params)

            if not item:
                return Response({"success": False, "detail": "There is no detail for {}".format(pk)},
                                status=status.HTTP_404_NOT_FOUND)
            else:

                try:
                    serializer = self.__class__.serializer_class(item, context={'request': request})
                    return Response(serializer.data)
                except Exception as e:
                    logger.error("Plugin error: {}".format(e))

        except DataSource.DoesNotExist:
            return Response({'success': False, 'detail': "There is no detail for datasource object {}.".format(pk)},
                            status=status.HTTP_404_NOT_FOUND, )
        except Exception as e:
            return Response({'success': False, 'detail': str(e)},
                            status=status.HTTP_404_NOT_FOUND, )


class MonitoringFeatureViewSet(MonitoringFeatureAccess, DataSourcePluginViewSet):
    """
    MonitoringFeature: A feature upon which monitoring is made. OGC Timeseries Profile OM_MonitoringFeature.

    **Properties**

    * *id:* string, Unique feature identifier
    * *name:* string, Feature name
    * *description:* string, Description of the feature
    * *feature_type:* sting, FeatureType: REGION, SUBREGION, BASIN, SUBBASIN, WATERSHED, SUBWATERSHED, SITE, PLOT, HORIZONTAL PATH, VERTICAL PATH, POINT
    * *observed_property_variables:* list of observed variables made at the feature. Observed property variables are configured via the plugins.
    * *related_sampling_feature_complex:* list of related_sampling features. PARENT features are currently supported.
    * *shape:* string, Shape of the feature: POINT, CURVE, SURFACE, SOLID
    * *coordinates:* location of feature in absolute and/or representative datum
    * *description_reference:* string, additional information about the Feature
    * *related_party:* (optional) list of people or organizations responsible for the Feature
    * *utc_offset:* float, Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    * *url:* url, URL with details for the feature

    **Filter** by the following attributes (/?attribute=parameter&attribute=parameter&...)

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)

    **Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)
    """
    serializer_class = MonitoringFeatureSerializer
    synthesis_model = MonitoringFeature

    @typing.no_type_check
    def list(self, request: Request, format: str = None) -> Response:
        return super().list(request=request, format=format)

    @typing.no_type_check
    def retrieve(self, request: Request, pk: str) -> Response:
        return super().retrieve(request=request, pk=pk)

    @action(detail=True, url_name='regions-detail')
    def regions(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subregions-detail')
    def subregions(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='basins-detail')
    def basins(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subbasins-detail')
    def subbasins(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='watersheds-detail')
    def watersheds(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='subwatersheds-detail')
    def subwatersheds(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='sites-detail')
    def sites(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='plots-detail')
    def plots(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='horizontalpaths-detail')
    def horizontalpaths(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='verticalpaths-detail')
    def verticalpaths(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)

    @action(detail=True, url_name='points-detail')
    def points(self, request, pk=None):
        return self.retrieve(request=request, pk=pk)


class MeasurementTimeseriesTVPObservationViewSet(MeasurementTimeseriesTVPObservationAccess,
                                                 DataSourcePluginViewSet):
    """
    MeasurementTimeseriesTVPObservation: Series of measurement (numerical) observations in
    TVP (time value pair) format grouped by time (i.e., a timeseries).

    **Properties**

    * *id:* string, Observation identifier (optional)
    * *type:* enum, MEASUREMENT_TVP_TIMESERIES
    * *observed_property:* url, URL for the observation's observed property
    * *phenomenon_time:* datetime, datetime of the observation, for a timeseries the start and end times can be provided
    * *utc_offset:* float, Coordinate Universal Time offset in hours (offset in hours), e.g., +9
    * *feature_of_interest:* MonitoringFeature obj, feature on which the observation is being made
    * *feature_of_interest_type:* enum (FeatureTypes), feature type of the feature of interest
    * *result_points:* list of TimeValuePair obj, observed values of the observed property being assessed
    * *time_reference_position:* enum, position of timestamp in aggregated_duration (START, MIDDLE, END)
    * *aggregation_duration:* enum, time period represented by observation (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
    * *unit_of_measurement:* string, units in which the observation is reported
    * *statistic:* enum, statistical property of the observation result (MEAN, MIN, MAX, TOTAL)
    * *result_quality:* enum, quality assessment of the result (CHECKED, UNCHECKED)

    **Filter** by the following attributes (?attribute=parameter&attribute=parameter&...):

    * *monitoring_features (required):* comma separated list of monitoring_features ids
    * *observed_property_variables (required):* comma separated list of observed property variable ids
    * *start_date (required):* date YYYY-MM-DD
    * *end_date (optional):* date YYYY-MM-DD
    * *aggregation_duration (default: DAY):* enum (YEAR|MONTH|DAY|HOUR|MINUTE|SECOND)
    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)

    **Restrict fields** with query parameter ‘fields’. (e.g. ?fields=id,name)


    """
    serializer_class = MeasurementTimeseriesTVPObservationSerializer
    synthesis_model = MeasurementTimeseriesTVPObservation

    @action(detail=False, url_path='measurement_tvp_timeseries', url_name='measurementtvptimeseries-list', methods=['GET'])
    def list(self, request: Request, format: str = None) -> Response:
        return super().list(request=request, format=format)
