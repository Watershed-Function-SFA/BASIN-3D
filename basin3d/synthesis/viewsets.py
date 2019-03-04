"""
`basin3d.synthesis.viewsets`
****************************

.. currentmodule:: basin3d.synthesis.viewsets

:synopsis: The BASIN-3D Synthesis Model Viewsets that support the REST api
:module author: Val Hendrix <vhendrix@lbl.gov>

View Controllers for BASIN-3D REST api

* :class:`DataSourcePluginViewSet` - Base ViewSet for all synthesized model views.
* :class:`DataPointGroupViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.measurement.DataPointGroup` objects
* :class:`DataPointViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.measurement.DataPoint` objects
* :class:`PlotViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Plot` objects
* :class:`PointLocationViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.PointLocation` objects
* :class:`RegionViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Region` objects
* :class:`SiteViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Site` objects

----------------------------------

"""
import logging

from basin3d.models import DataSource
from basin3d.plugins import InvalidOrMissingCredentials

from basin3d.synthesis.models.field import Region, Site, Plot, PointLocation
from basin3d.synthesis.models.measurement import MeasurementTimeseriesTVPObservation, TimeMetadataMixin
from basin3d.synthesis.query import extract_id, extract_query_param_ids, \
    QUERY_PARAM_OBSERVED_PROPERTY_VARIABLES, QUERY_PARAM_AGGREGATION_DURATION, \
    QUERY_PARAM_LOCATIONS, QUERY_PARAM_REGIONS, QUERY_PARAM_SITES, \
    QUERY_PARAM_RESULT_QUALITY

from basin3d.synthesis.serializers import RegionSerializer, SiteSerializer, \
    MeasurementTimeseriesTVPObservationSerializer, \
    PlotSerializer, PointLocationSerializer
from rest_framework import status
from rest_framework import versioning
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DataSourcePluginViewSet(ViewSet):
    """
    Base ViewsSet  for all DataSource plugins

    """
    versioning_class = versioning.NamespaceVersioning

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """
        # do nothing, subclasses may override this
        return request.query_params

    def list(self, request, format=None):
        """
        Return the synthesized plugin results
        """
        items = []

        # Are we filtering by Datasource?
        if 'datasource' in request.query_params.keys():
            datasources = DataSource.objects.filter(id_prefix=request.query_params['datasource'])
        else:
            datasources = DataSource.objects.all()

        # Iterate over the plugins
        # (Consider parallelizing this, and using a StreamingHttpResponse )
        for datasource in datasources: # Get the plugin model

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
                    except InvalidOrMissingCredentials as e:
                        logger.error(e)

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a single synthesized value
        :param request:
        :param pk:
        :return:
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


class RegionViewSet(DataSourcePluginViewSet):
    """
    Return a Region

    **Fields**

    * *id* - unique identifier
    * *name* - site name
    * *geom* - site geometry
    * *description*
    * *url* - for detail on a single region

    ** Filter results** by the following attributes

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)

    ** Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)


    """
    serializer_class = RegionSerializer
    synthesis_model = Region


class SiteViewSet(DataSourcePluginViewSet):
    """
    Retrieve Sites. A demarcated, geographic area where measurements are being c
    onducted. E.g. East River Site, K34-Manaus.

    *Note: Site differs from ODM 2 definition of a site, which is a point location.*

    **Fields**

    * *id* - unique identifier
    * *name* - Site name
    * *description*
    * *country*
    * *state_province*
    * *utc_offset*
    * *center_coordinates* - where the site is located
    * *contacts* - list of site contacts
    * *pi* - program investigator
    * *urls* - websites urls
    * *url* - returns a single site record


    ** Filter results** by the following attributes:

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)
    * *regions (optional):* comma separated list of region ids (e.g ?regions=`region.id`)

    ** Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)

    """
    serializer_class = SiteSerializer
    synthesis_model = Site

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + region

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """
        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_REGIONS,
                                id_prefix=id_prefix,
                                query_params=query_params)

        return query_params


class PlotViewSet(DataSourcePluginViewSet):
    """
    Retrieve Plots

    **Fields**

    * *id* - unique identifier
    * *name* - Plot name
    * *description*
    * *geom* - the geometry of the plot
    * *pi* - program investigator
    * *url* - returns a single plot record


    ** Filter results** by the following attributes:

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)
    * *regions (optional):* comma separated list of region ids (e.g ?regions=`region.id`)
    * *sites (optional)* comma separated list of site ids (e.g ?sites=`site.id`)

    ** Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)

    """
    serializer_class = PlotSerializer
    synthesis_model = Plot

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + site
          + region

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """
        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_SITES,
                                id_prefix=id_prefix,
                                query_params=query_params)

        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_REGIONS,
                                id_prefix=id_prefix,
                                query_params=query_params)

        return query_params


class PointLocationViewSet(DataSourcePluginViewSet):
    """
    Retrieve Point Locations

    **Fields**

    * *id* - unique identifier
    * *name* - point location name
    * *description*
    * *site* - the site associated with this point location
    * *horizontal_position* - the depth of this point location
    * *url* - returns a single point location record
    * *observed_property_variables* - a list of available observed property variables


    ** Filter results**  by the following attributes:

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)
    * *sites (optional)* comma separated list of site ids (e.g ?sites=`site.id`)

    ** Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)


    """
    serializer_class = PointLocationSerializer
    synthesis_model = PointLocation

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + site
          + region

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """
        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_SITES,
                                id_prefix=id_prefix,
                                query_params=query_params)

        return query_params


class MeasurementTimeseriesTVPObservationViewSet(DataSourcePluginViewSet):
    """
    Retrieve MeasurementTimeseriesTVPObservation Groups

    ** Properties **

    * *observation_property:* string, (optional)
    * *start_time:* datetime,  survey start time
    * *end_time:* datetime, units: survey end time
    * *utc_offset:* float (offset in hours), +9
    * *geographical_group_id:* identifier for the geographical group
    * *geographical_group_type* enum (sampling_feature, site, plot,
            region, point_location, measurement position)
    * *result_points* -- for the list of data_points associated with this Data Point Group

    ** Filter results** by the following attributes:

    * *datasource (optional):* a single data source id prefix (e.g ?datasource=`datasource.id_prefix`)
    * *locations (required)* comma separated list of locations ids
    * *observed_property_variables (required)* comma separated list of observed property variable ids
    * *start_date (required)*
    * *end_date*
    * *aggregation_duration (default:day):*  options (year|month|day|hour|minute|second)
    * *result_quality* if 'True' then filter by quality checked data. Otherwise, there is no filtering.

    ** Restrict fields**  with query parameter ‘fields’. (e.g. ?fields=id,name)


    """
    serializer_class = MeasurementTimeseriesTVPObservationSerializer
    synthesis_model = MeasurementTimeseriesTVPObservation

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + locations
          + observed_property_variables
          + temporal_resolution (default: day)
          + quality_checked

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """

        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        extract_query_param_ids(request=request,
                                param_name=QUERY_PARAM_LOCATIONS,
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
