import logging

import djangoplugins
from basin3d.models import DataSource
from basin3d.synthesis.models import Region
from basin3d.synthesis.models.simulations import Model
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer
from basin3d.tests.test_synthesis_models import ModelDomain
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
    plugin_generator_method = str()
    plugin_retrieve_method = str()

    def list(self, request, format=None):
        """
        Return the synthesized plugin results
        """
        items = []
        datasources = DataSource.objects.all()

        # Iterate over the plugins
        # (Consider parallelizing this, and using a StreamingHttpResponse )
        for datasource in datasources:
            plugin_model = datasource.plugin  # Get the plugin model

            if plugin_model.status == djangoplugins.models.ENABLED:

                plugin_views = plugin_model.get_plugin().get_plugin_views()
                if self.synthesis_model in plugin_views:
                    for obj in plugin_views[self.synthesis_model].list(request):
                        items.append(obj)

        serializer = self.__class__.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a single syntheized value
        :param request:
        :param pk:
        :return:
        """
        datasources = DataSource.objects.all()
        obj = None
        for datasource in datasources:
            plugin_model = datasource.plugin  # Get the plugin model
            if plugin_model.status == djangoplugins.models.ENABLED:

                plugin_views = plugin_model.get_plugin().get_plugin_views()
                if self.synthesis_model in plugin_views:
                    obj = plugin_views[self.synthesis_model].get(request, pk=pk)
                    if obj:  # probably want to be smarter about this.  Do we used an id prefix?
                        break
        if obj:
            try:
                serializer = self.__class__.serializer_class(obj, context={'request': request})
                return Response(serializer.data)
            except Exception as e:
                logger.error("Plugin error: ({},{}) -- {}".format(plugin_model.name,
                                                                  self.__class__.plugin_retrieve_method,
                                                                  e))

        return Response({"success": False, "content": "There is no detail for {}".format(pk)})


class RegionsViewSet(DataSourcePluginViewSet):
    """
    Return a Region
    """
    serializer_class = RegionSerializer
    synthesis_model = Region


class ModelViewSet(DataSourcePluginViewSet):
    """
    Return a Model
    """
    serializer_class = ModelSerializer
    synthesis_model = Model


class ModelDomainViewSet(DataSourcePluginViewSet):
    """
    Return a Model Domain
    """
    serializer_class = ModelDomainSerializer
    synthesis_model = ModelDomain
