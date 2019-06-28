"""
`basin3d.synthesis.viewsets`
****************************

.. currentmodule:: basin3d.synthesis.viewsets

:synopsis: BASIN-3D Synthesis Model Viewsets (View Controllers) that support the REST API
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>


Below is the inheritance diagram for BASIN-3D Viewsets.  All of the views are based on
:class:`DataSourcePluginViewSet` which provide all the synthesis logic for viewing data
from the connected data sources.

.. inheritance-diagram:: basin3d.synthesis.viewsets
    :top-classes: basin3d.synthesis.viewsets.DataSourcePluginViewSet
    :parts: 2

----------------------------------

"""
import logging
from typing import Dict

from basin3d.models import DataSource, FeatureTypes
from basin3d.plugins import InvalidOrMissingCredentials, get_request_feature_type

from basin3d.synthesis.models.field import MonitoringFeature
from basin3d.synthesis.models.measurement import MeasurementTimeseriesTVPObservation, TimeMetadataMixin
from basin3d.synthesis.query import extract_query_param_ids, \
    QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES, QUERY_PARAM_AGGREGATION_DURATION, \
    QUERY_PARAM_MONITORING_FEATURES, QUERY_PARAM_RESULT_QUALITY, QUERY_PARAM_REGIONS, QUERY_PARAM_SUBBASINS

from basin3d.synthesis.serializers import MonitoringFeatureSerializer, \
    MeasurementTimeseriesTVPObservationSerializer
from rest_framework import status
from rest_framework import versioning
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DataSourcePluginViewSet(ViewSet):
    """
    Base ViewsSet for all DataSource plugins.  The inheritance diagram shows that this class extends the
    `Django Rest Framework <https://www.django-rest-framework.org/>`_
    class :class:`rest_framework.viewsets.ViewSet`. These are based on `Django generic views
    <https://docs.djangoproject.com/en/2.2/topics/class-based-views/generic-display/>`_.

    .. inheritance-diagram:: rest_framework.viewsets.ViewSet basin3d.synthesis.viewsets.DataSourcePluginViewSet

    """
    versioning_class = versioning.NamespaceVersioning

    def synthesize_query_params(self, request, plugin_view: 'DataSourcePluginViewSet') -> Dict[str, str]:
        """
        Synthesizes query parameters, if necessary

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return: The query parameters
        """
        # do nothing, subclasses may override this
        return request.query_params

    def list(self, request: Request, format:str = None) -> Response:
        """
        Return the synthesized plugin results

        :param request: The incoming request object
        :type request: :class:`rest_framework.request.Request`
        :param format: The format to present the data (default is json)
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """
        items = []

        # Are we filtering by Datasource?
        if 'datasource' in request.query_params.keys():
            datasources = DataSource.objects.filter(id_prefix=request.query_params['datasource'])
        else:
            datasources = DataSource.objects.all()

        # Iterate over the plugins
        # (Consider parallelizing this, and using a StreamingHttpResponse )
        for datasource in datasources:  # Get the plugin model

            if datasource.enabled:

                plugin_views = datasource.get_plugin().get_plugin_views()
                if self.synthesis_model in plugin_views and \
                        hasattr(plugin_views[self.synthesis_model], "list"):
                    try:
                        for obj in plugin_views[self.synthesis_model].list(request,
                                                                           **self.synthesize_query_params(
                                                                               request,
                                                                               plugin_views[
                                                                                   self.synthesis_model])
                                                                           ):
                            items.append(obj)
                            logger.debug(self.synthesize_query_params(request, plugin_views[self.synthesis_model]))
                    except InvalidOrMissingCredentials as e:
                        logger.error(e)

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request: Request, pk: str = None) -> Response:
        """
        Retrieve a single synthesized value

        :param request: The request object
        :type request: :class:`rest_framework.request.Request`
        :param pk: The primary key
        :return: The HTTP Response
        :rtype: :class:`rest_framework.request.Response`
        """

        # split the datasource id prefix from the primary key
        pk_list = pk.split("-")
        try:
            datasource = DataSource.objects.get(id_prefix=pk_list[0])
            obj = None
            if datasource:
                datasource_pk = pk.replace("{}-".format(pk_list[0]),
                                           "", 1)  # The datasource id prefix needs to be removed
                if datasource.enabled:

                    plugin_views = datasource.get_plugin().get_plugin_views()
                    if self.synthesis_model in plugin_views:
                        obj = plugin_views[self.synthesis_model].get(request, pk=datasource_pk)
            if obj:
                try:
                    serializer = self.__class__.serializer_class(obj, context={'request': request})
                    return Response(serializer.data)
                except Exception as e:
                    logger.error("Plugin error: ({},{}) -- {}".format(datasource.name,
                                                                      self.action,
                                                                      e))

            return Response({"success": False, "content": "There is no detail for {}".format(pk)},
                            status=status.HTTP_404_NOT_FOUND)
        except DataSource.DoesNotExist:
            return Response({'success': False, 'detail': "There is no detail for datasource object {}. "
                                                         "The datasource id '{}' is invalid.".format(pk, pk_list[0])},
                            status=status.HTTP_404_NOT_FOUND, )


class MonitoringFeatureViewSet(DataSourcePluginViewSet):
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

    def synthesize_query_params(self, request: Request, plugin_view: DataSourcePluginViewSet) -> Dict[str, str]:
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:

        :param request: the request to synthesize
        :type request: :class:`rest_framework.request.Request`
        :param plugin_view: The plugin view to synthesize query params for
        :return: The query parameters
        """
        query_params = {}

        # Look in Request to find URL and get type out if there
        # ToDo: potentially remove -- need to figure out how to handle in plugin
        k, _ = self.extract_type(request)
        if k is not None:
            query_params["feature_type"] = k

        for key, value in request.query_params.items():
            query_params[key] = value

        id_prefix = plugin_view.datasource.id_prefix
        for param_name in [QUERY_PARAM_MONITORING_FEATURES, QUERY_PARAM_REGIONS, QUERY_PARAM_SUBBASINS]:
            extract_query_param_ids(request=request,
                                    param_name=param_name,
                                    id_prefix=id_prefix,
                                    query_params=query_params)

        return query_params

    def extract_type(self, request):
        """
        Extract the feature types from the request

        :param request: The Request object
        :return: Tuple `(feature_type_code, feature_type_name)`. (e.g (0, 'REGION')
        :rtype: tuple

        """
        k = get_request_feature_type(request)
        if k:
            return k, FeatureTypes.TYPES[k]
        return None, None

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


class MeasurementTimeseriesTVPObservationViewSet(DataSourcePluginViewSet):
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

    def synthesize_query_params(self, request: Request, plugin_view: DataSourcePluginViewSet) -> Dict[str, str]:
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + monitoring_features
          + observed_property_variables
          + aggregation_duration (default: DAY)
          + quality_checked

        :param request: the request to synthesize
        :type request: :class:`rest_framework.request.Request`
        :param plugin_view: The plugin view to synthesize query params for
        :return: The query parameters
        """

        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        # ToDo: Change to monitoring feature
        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_MONITORING_FEATURES,
                                id_prefix=id_prefix,
                                query_params=query_params)

        # Synthesize ObservedPropertyVariable (from BASIN-3D to DataSource variable name)
        if QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES in request.query_params:
            observed_property_variables = request.query_params.get(QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES, '').split(",")
            query_params[QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES] = plugin_view.get_observed_property_variables(
                observed_property_variables, from_basin3d=True)
        # Set the default Aggregation Duration
        if QUERY_PARAM_AGGREGATION_DURATION not in request.query_params:
            query_params[
                QUERY_PARAM_AGGREGATION_DURATION] = TimeMetadataMixin.AGGREGATION_DURATION_DAY

        if QUERY_PARAM_RESULT_QUALITY in request.query_params:
            query_params[
                QUERY_PARAM_RESULT_QUALITY] = request.query_params[QUERY_PARAM_RESULT_QUALITY] in ["true", "True"]

        return query_params
