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
* :class:`MeshViewSet` - supports REST ``GET`` methods that synthesize :class:`~basin3d.synthesis.models.simulations.Mesh` objects
* :class:`ModelDomainViewSet` - supports REST ``GET`` methods that synthesize :class:`~basin3d.synthesis.simulations.ModelDomain` objects
* :class:`ModelRunViewSet` - supports REST ``GET`` methods that synthesize :class:`~basin3d.synthesis.simulations.ModelRun` objects
* :class:`ModelViewSet` - supports REST ``GET`` methods that synthesize :class:`~basin3d.synthesis.models.simulations.Model` objects
* :class:`PlotViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Plot` objects
* :class:`PointLocationViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.PointLocation` objects
* :class:`RegionViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Region` objects
* :class:`SiteViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.field.Site` objects

----------------------------------

"""
import logging

import djangoplugins
from basin3d.models import DataSource
from basin3d.plugins import InvalidOrMissingCredentials
from basin3d.synthesis.models.field import Region, Site, Plot, PointLocation
from basin3d.synthesis.models.measurement import DataPointGroup, DataPoint, TimeSeriesDataPoint
from basin3d.synthesis.models.simulations import Model, ModelDomain, Mesh, ModelRun
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer, MeshSerializer, \
    DataPointGroupSerializer, ModelRunSerializer, DataPointSerializer, SiteSerializer, \
    PlotSerializer, PointLocationSerializer
from rest_framework import status
from rest_framework import versioning
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

QUERY_PARAM_LOCATIONS = "locations"
QUERY_PARAM_MEASURE_VARIABLES = "measure_variables"
QUERY_PARAM_TEMPORAL_RESOLUTION = "temporal_resolution"
QUERY_PARAM_START_DATE = "start_date"
QUERY_PARAM_END_DATE = "end_date"

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
        for datasource in datasources:
            plugin_model = datasource.plugin  # Get the plugin model

            if plugin_model.status == djangoplugins.models.ENABLED:

                plugin_views = plugin_model.get_plugin().get_plugin_views()
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
                plugin_model = datasource.plugin  # Get the plugin model
                if plugin_model.status == djangoplugins.models.ENABLED:

                    plugin_views = plugin_model.get_plugin().get_plugin_views()
                    if self.synthesis_model in plugin_views:
                        obj = plugin_views[self.synthesis_model].get(request, pk=datasource_pk)
            if obj:
                try:
                    serializer = self.__class__.serializer_class(obj, context={'request': request})
                    return Response(serializer.data)
                except Exception as e:
                    logger.error("Plugin error: ({},{}) -- {}".format(plugin_model.name,
                                                                      self.__class__.plugin_retrieve_method,
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

    * ** URLS **
      * *url* -- for detail on a single DataPoint Group
      * *model_domains* -- for the list of model domains associated with this Region
    """
    serializer_class = RegionSerializer
    synthesis_model = Region

    @detail_route()  # Custom Route for an association
    def model_domains(self, request, pk=None):
        """
        Retrieve the Model Domains  for a Region.

        Maps to  /regions/{pk}/model_domains/

        :param request:
        :param pk:
        :return:
        """
        id_prefix = pk.split("-")[0]
        try:
            datasource = DataSource.objects.get(id_prefix=id_prefix)
            items = []

            if datasource:
                plugin_model = datasource.plugin  # Get the plugin model

                if plugin_model.status == djangoplugins.models.ENABLED:

                    plugin_views = plugin_model.get_plugin().get_plugin_views()
                    if self.synthesis_model in plugin_views:
                        request.GET = request.GET.copy()  # Make the request mutable
                        request.GET["region_id"] = pk.replace("{}-".format(id_prefix),
                                                              "",
                                                              1)  # The datasource id prefix needs to be removed
                        for obj in plugin_views[ModelDomain].list(request):
                            items.append(obj)

            serializer = ModelDomainViewSet.serializer_class(items, many=True, context={'request': request})
            return Response(serializer.data)

        except DataSource.DoesNotExist:
            return Response({'success': False, 'detail': "There is no detail for datasource object {}. "
                                                         "The datasource id '{}' is invalid.".format(pk, id_prefix)},
                            status=status.HTTP_404_NOT_FOUND, )


class SiteViewSet(DataSourcePluginViewSet):
    """
    Retrieve Sites

    ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    """
    serializer_class = SiteSerializer
    synthesis_model = Site


class PlotViewSet(DataSourcePluginViewSet):
    """
    Retrieve Plots

    ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    """
    serializer_class = PlotSerializer
    synthesis_model = Plot


class PointLocationViewSet(DataSourcePluginViewSet):
    """
    Retrieve Point Locations

    ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    """
    serializer_class = PointLocationSerializer
    synthesis_model = PointLocation


class ModelViewSet(DataSourcePluginViewSet):
    """
    Retrieve Models

    * ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    """
    serializer_class = ModelSerializer
    synthesis_model = Model


class MeshViewSet(DataSourcePluginViewSet):
    """
    Return a Mesh

    * ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    """
    serializer_class = MeshSerializer
    synthesis_model = Mesh


class ModelDomainViewSet(DataSourcePluginViewSet):
    """
    Return a Model Domain

    ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    * ** URLS **
      * *url* -- for detail on a single Model Domain
      * *meshes* -- for the list of meshes associated with this Model Domain
    """
    serializer_class = ModelDomainSerializer
    synthesis_model = ModelDomain

    @detail_route()  # Custom Route for an association
    def meshes(self, request, pk=None):
        """
        Retrieve the Meshes  for a Model Domain.

        Maps to  /model_domains/{pk}/meshes/

        :param request:
        :param pk:
        :return:
        """
        id_prefix = pk.split("-")[0]
        try:
            datasource = DataSource.objects.get(id_prefix=id_prefix)

            items = []

            if datasource:
                plugin_model = datasource.plugin  # Get the plugin model

                if plugin_model.status == djangoplugins.models.ENABLED:

                    plugin_views = plugin_model.get_plugin().get_plugin_views()
                    if self.synthesis_model in plugin_views:
                        request.GET = request.GET.copy()  # Make the request mutable
                        request.GET["model_domain_id"] = pk.replace("{}-".format(id_prefix),
                                                                    "",
                                                                    1)  # The datasource id prefixe needs to be removed
                        for obj in plugin_views[Mesh].list(request):
                            items.append(obj)

            serializer = MeshViewSet.serializer_class(items, many=True, context={'request': request})
            return Response(serializer.data)
        except DataSource.DoesNotExist:
            return Response({'success': False, 'detail': "There is no detail for datasource object {}. "
                                                         "The datasource id '{}' is invalid.".format(pk, id_prefix)},
                            status=status.HTTP_404_NOT_FOUND, )


class ModelRunViewSet(DataSourcePluginViewSet):
    """
    Return a Model Runs
    """
    serializer_class = ModelRunSerializer
    synthesis_model = ModelRun


class DataPointGroupViewSet(DataSourcePluginViewSet):
    """
    Retrieve  Data Point Groups

    * ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    * ** URLS **
          * *url* -- for detail on a single Data Point Group
          * *data_points* -- for the list of data_points associated with this Data Point Group

    """
    serializer_class = DataPointGroupSerializer
    synthesis_model = DataPointGroup

    @detail_route()  # Custom Route for an association
    def datapoints(self, request, pk=None):
        """
        Retrieve the Meshes  for a Model Domain.

        Maps to  /model_domains/{pk}/meshes/

        :param request:
        :param pk:
        :return:
        """
        id_prefix = pk.split("-")[0]
        try:
            datasource = DataSource.objects.get(id_prefix=id_prefix)

            items = []

            if datasource:
                plugin_model = datasource.plugin  # Get the plugin model

                if plugin_model.status == djangoplugins.models.ENABLED:

                    plugin_views = plugin_model.get_plugin().get_plugin_views()
                    if self.synthesis_model in plugin_views:
                        request.GET = request.GET.copy()  # Make the request mutable
                        request.GET["datapoint_group_id"] = pk.replace("{}-".format(id_prefix),
                                                                       "",
                                                                       1)  # The datasource id prefixe needs to be removed
                        for obj in plugin_views[DataPoint].list(request):
                            items.append(obj)

            serializer = DataPointViewSet.serializer_class(items, many=True,
                                                      context={'request': request})
            return Response(serializer.data)
        except DataSource.DoesNotExist:
            return Response(
                {'success': False, 'detail': "There is no detail for datasource object {}. "
                                             "The datasource id '{}' is invalid.".format(pk,
                                                                                         id_prefix)},
                status=status.HTTP_404_NOT_FOUND, )


class DataPointViewSet(DataSourcePluginViewSet):
    """
    Search for Data Points

    * ** Filter results ** by datasource (e.g ?datasource=<datasource.id_prefix>)
    * ** Search Parameters **
        * *locations - * comma separated list of locations ids
        * *measure_variables - * comma separated list of variable ids
        * *temporal_resolution (default:day) - *  options (year|month|day|hour|minute|second)
        * *start_date*
        * *end_date*




    """

    serializer_class = DataPointSerializer
    synthesis_model = DataPoint

    def synthesize_query_params(self, request, plugin_view):
        """
        Synthesizes query parameters, if necessary

        Parameters Synthesized:
          + locations
          + measure_variables
          + temporal_resolution (default: day)

        :param request: the request to synthesize
        :param plugin_view: The plugin view to synthesize query params for
        :return:
        """

        id_prefix = plugin_view.datasource.id_prefix
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        # Synthesize the locations (remove datasource id_prefix)
        if QUERY_PARAM_LOCATIONS in request.query_params:
            locations = request.query_params.get(QUERY_PARAM_LOCATIONS, None)

            if locations:
                query_params[QUERY_PARAM_LOCATIONS] = [x.replace("{}-".format(id_prefix),
                                                                 "", 1) for x in
                                                       locations.split(",")
                                                       if x.startswith("{}-".format(id_prefix))]

        # Synthesize MeasurementVariable (from BASIN-3D to DataSource variable name)
        if QUERY_PARAM_MEASURE_VARIABLES in request.query_params:
            measure_variables = request.query_params.get(QUERY_PARAM_MEASURE_VARIABLES, '').split(
                ",")
            query_params[QUERY_PARAM_MEASURE_VARIABLES] = plugin_view.get_variables(
                measure_variables,
                from_basin3d=True)
        # Set the default Temporal Resolution
        if QUERY_PARAM_TEMPORAL_RESOLUTION not in request.query_params:
            query_params[
                QUERY_PARAM_TEMPORAL_RESOLUTION] = TimeSeriesDataPoint.TEMPORAL_RESOLUTION_DAY

        return query_params
