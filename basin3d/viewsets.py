import json
import logging

import djangoplugins
from basin3d.models import MeasurementVariable, DataSource, DataSourceMeasurementVariable
from basin3d.serializers import DataSourceSerializer, MeasurementVariableSerializer, \
    DataSourceMeasurementVariableSerializer
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class DirectAPIViewSet(viewsets.GenericViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    lookup_field = 'id_prefix'

    def retrieve(self, request, *args, **kwargs):
        """ direct call to API"""

        datasource = self.get_object()

        plugin_model = datasource.plugin  # Get the plugin model

        if plugin_model.status == djangoplugins.models.ENABLED:
            direct_path = ""
            if "direct_path" in kwargs.keys():
                direct_path = kwargs["direct_path"]

            plugin = plugin_model.get_plugin()
            if hasattr(plugin, "direct"):
                response = plugin.direct(request, direct_path)
                return Response(
                    data=json.loads(response.content.replace(datasource.location,
                                                             request.build_absolute_uri(
                                                                 reverse('direct-path-detail',
                                                                         kwargs={
                                                                             "id_prefix": datasource.id_prefix,
                                                                             "direct_path": ""})))),
                    status=response.status)

        return Response(status=status.HTTP_404_NOT_FOUND)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of all  Data Sources available to the BASIN-3D service

        The detail view will return a direct call to the data source itself

    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

    @detail_route()  # Custom Route for an association
    def src_parameters(self, request, pk=None):
        """
        Retrieve the DataSource Parameters for a broker parameter.

        Maps to  /datasources/{pk}/map/

        :param request:
        :param pk:
        :return:
        """
        params = DataSourceMeasurementVariable.objects.filter(datasource=pk)

        # `HyperlinkedRelatedField` requires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = DataSourceMeasurementVariableSerializer(params, many=True,
                                                             context={'request': request})
        return Response(serializer.data)


class MeasurementVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of available BASIN-3D MeasurementVariables

    """
    queryset = MeasurementVariable.objects.all()
    serializer_class = MeasurementVariableSerializer
    filter_backends = (filters.DjangoFilterBackend,)

    @detail_route()  # Custom Route for an association
    def measure_variables(self, request, pk=None):
        """
        Retrieve the DataSource Parameters for a broker parameter.

        Maps to  /measure_variables/{pk}/map/

        :param request:
        :param pk: measure_variables primary key
        :return:
        """
        params = DataSourceMeasurementVariable.objects.filter(measure_variable=pk)

        # `HyperlinkedRelatedField` requires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = DataSourceMeasurementVariableSerializer(params, many=True,
                                                             context={'request': request})
        return Response(serializer.data)
