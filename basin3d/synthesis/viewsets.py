"""
`basin3d.synthesis.models.viewsets`
***********************************

.. currentmodule:: basin3d.synthesis.models.viewsets

:synopsis: The BASIN-3D Synthesis Model Viewsets that support the REST api
:module author: Val Hendrix <vhendrix@lbl.gov>

Controllers for BASIN-3D REST api

* :class:`DataSourcePluginViewSet` - Base ViewSet for all synthesized model views.
* :class:`RegionViewSet` - supports REST `GET` methods that synthesize :class:`~basin3d.synthesis.models.field.Region`s
* :class:`ModelViewSet` - supports REST `GET` methods that synthesize :class:`~basin3d.synthesis.models.simulations.Model`s
* :class:`MeshViewSet` - supports REST `GET` methods that synthesize :class:`~basin3d.synthesis.models.simulations.Mesh`es
* :class:`ModelDomainViewSet` - supports REST `GET` methods that synthesize :class:`~basin3d.synthesis.simulations.ModelDomains`s

----------------------------------

"""
import logging

import djangoplugins
from basin3d.models import DataSource
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.simulations import Model, ModelDomain, Mesh
from basin3d.synthesis.serializers import RegionSerializer, ModelSerializer, ModelDomainSerializer, MeshSerializer
from rest_framework import versioning
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DataSourcePluginViewSet(ViewSet):
    """
    Base ViewsSet  for all DataSource plugins

    """
    versioning_class = versioning.NamespaceVersioning

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
        pk_list = pk.split("-")
        datasource = DataSource.objects.get(id_prefix=pk_list[0])
        obj = None
        if datasource:
            datasource_pk = pk.replace("{}-".format(pk_list[0]), "")  # The datasource id prefixe needs to be removed
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


class MeshViewSet(DataSourcePluginViewSet):
    """
    Return a Model Domain
    """
    serializer_class = MeshSerializer
    synthesis_model = Mesh


class ModelDomainViewSet(DataSourcePluginViewSet):
    """
    Return a Model Domain
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
        datasource = DataSource.objects.get(id_prefix=id_prefix)
        items = []

        if datasource:
            plugin_model = datasource.plugin  # Get the plugin model

            if plugin_model.status == djangoplugins.models.ENABLED:

                plugin_views = plugin_model.get_plugin().get_plugin_views()
                if self.synthesis_model in plugin_views:
                    request.GET = request.GET.copy()  # Make the request mutable
                    request.GET["model_domain_id"] = pk.replace("{}-".format(id_prefix),
                                                                "")  # The datasource id prefixe needs to be removed
                    for obj in plugin_views[Mesh].list(request):
                        items.append(obj)

        serializer = MeshViewSet.serializer_class(items, many=True, context={'request': request})
        return Response(serializer.data)
