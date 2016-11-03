import djangoplugins
import logging

from rest_framework import versioning
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from basin3d.models import DataSource
from basin3d.synthesis.serializers import LocationSerializer, DataPointSerializer, SiteSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


class PluginViewSet(ViewSet):
    versioning_class = versioning.NamespaceVersioning
    plugin_generator_method = str()
    plugin_retrieve_method = str()

    def list(self, request, format=None):
        """
        Return a hardcoded response.
        """
        items = []
        datasources = DataSource.objects.all()

        # Iterate over the plugins
        # (Consider parallelizing this, and using a StreamingHttpResponse )
        for datasource in datasources:
            plugin_model = datasource.plugin  # Get the plugin model

            if plugin_model.status == djangoplugins.models.ENABLED:

                if self.__class__.plugin_generator_method:
                    # Get the Plugin generator method to execute
                    plugin_generator = getattr(plugin_model.get_plugin(),
                                               self.__class__.plugin_generator_method)(datasource, **request.query_params)
                    if plugin_generator:
                        try:
                            for item in plugin_generator:
                                items.append(item)
                        except Exception as e:
                            logger.error("Plugin error: ({},{}) -- {}".format(plugin_model.name,
                                                                              self.__class__.plugin_generator_method,
                                                                              e))

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        datasources = DataSource.objects.all()
        for datasource in datasources:
            plugin_model = datasource.plugin  # Get the plugin model
            if plugin_model.status == djangoplugins.models.ENABLED:

                if self.__class__.plugin_retrieve_method:
                    site = getattr(plugin_model.get_plugin(), self.__class__.plugin_retrieve_method)(datasource, pk)
                    if site:
                        try:
                            serializer = self.__class__.serializer_class(site, context={'request': request})
                            return Response(serializer.data)
                        except Exception as e:
                            logger.error("Plugin error: ({},{}) -- {}".format(plugin_model.name,
                                                                              self.__class__.plugin_generator_method,
                                                                              e))

        return Response({"success": False, "content": "There is no detail for {}".format(pk)})


class SitesViewSet(PluginViewSet):
    """
    Return a site
    """
    serializer_class = SiteSerializer
    plugin_generator_method = 'get_sites'
    plugin_retrieve_method = 'get_site'


class SearchViewSet(PluginViewSet):
    """
    Return a site
    """
    serializer_class = DataPointSerializer
    plugin_generator_method = 'get_data_points'
    plugin_retrieve_method = 'get_data_point'


class LocationsViewSet(PluginViewSet):
    """
    Return Locations
    """
    serializer_class = LocationSerializer
    plugin_generator_method = 'get_locations'
    plugin_retrieve_method = 'get_location'