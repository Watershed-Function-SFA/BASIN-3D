import logging

from rest_framework import filters, versioning
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from basin3d.models import MeasurementVariable, DataSource, DataSourceMeasurementVariable
from basin3d.serializers import DataSourceSerializer, MeasurementVariableSerializer, \
    DataSourceMeasurementVariableSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of all  Data Sources available to the wfsfa_broker service

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
        serializer = DataSourceMeasurementVariableSerializer(params, many=True, context={'request': request})
        return Response(serializer.data)


class MeasurementVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of available Data Broker parameters

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
        serializer = DataSourceMeasurementVariableSerializer(params, many=True, context={'request': request})
        return Response(serializer.data)


