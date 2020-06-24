"""
`django_basin3d.viewsets`
******************

.. currentmodule:: django_basin3d.viewsets

:platform: Unix, Mac
:synopsis: BASIN-3D ViewSets
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

Below is the inheritance diagram for BASIN-3D Viewsets.  All of the views are based on viewsets from
:class:`rest_framework.viewsets` which provide functionality for controlling access to the REST API.

.. inheritance-diagram:: django_basin3d.viewsets
    :top-classes: rest_framework.viewsets.GenericViewSet, rest_framework.viewsets.ReadOnlyModelViewSet


"""
import logging

import django_filters
from rest_framework.decorators import action

from django_basin3d import get_url
from django_basin3d.models import DataSource, ObservedProperty, ObservedPropertyVariable, \
    DataSourceObservedPropertyVariable
from django_basin3d.serializers import DataSourceSerializer, \
    ObservedPropertySerializer, ObservedPropertyVariableSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of all Data Sources available to the BASIN-3D service

        **Properties**

        * *name:* string, Unique name for the Data Source
        * *id_prefix:* string, unique id prefix for all Data Source ids
        * *location:* string, Location of the Data Source
        * *url:* url, Endpoint for Data Source
        * *observed_property_variables:* url, Observed property variables for Data Source
        * *check:* url, Validate the Data Source connection

    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

    @action(detail=True)
    def check(self, request, pk=None):
        """
        Determine if Datasource is available
        :param request:
        :param pk:
        :return:
        """

        datasource = self.get_object()

        plugin = datasource.get_plugin()

        if hasattr(plugin.get_meta(), "connection_class"):
            http_auth = plugin.get_meta().connection_class(datasource)

            try:
                http_auth.login()
                return Response(data={"message": "Login to {} data source was successful".format(datasource.name),
                                      "success": True},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={"message": str(e), "success": False},
                                status=status.HTTP_200_OK)

            finally:
                http_auth.logout()
        else:
            try:
                response = get_url("{}".format(datasource.location))

                if response.status_code == status.HTTP_200_OK:
                    return Response(
                        data={"message": "Response from {} data source was successful".format(datasource.name),
                              "success": True},
                        status=status.HTTP_200_OK)
                else:
                    return Response(
                        data={
                            "message": "Response from {} data source returns HTTP status {}".format(datasource.name,
                                                                                                    response.status_code),
                            "success": True},
                        status=status.HTTP_200_OK)

            except Exception as e:
                return Response(data={"message": str(e), "success": False},
                                status=status.HTTP_200_OK)

    @action(detail=True)  # Custom Route for an association
    def observed_property_variables(self, request, pk=None):
        """
        Retrieve the DataSource Parameters for a broker parameter.

        Maps to  /datasources/{pk}/observedpropertyvariables/

        :param request:
        :param pk:
        :return:
        """
        params = DataSourceObservedPropertyVariable.objects.filter(datasource=pk)
        v = []
        for dsmv in params:
            v.append(dsmv.observed_property_variable)

        # `HyperlinkedRelatedField` requires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = ObservedPropertyVariableSerializer(
            v, many=True, context={'request': request})
        return Response(serializer.data)


class ObservedPropertyVariableViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of available Observed Property Variables. A observed property variable defines what is
        being measured. See http://vocabulary.odm2.org/variablename/ for controlled vocabulary.

        **Properties**

        * *id:* string, Unique observed property variable identifier
        * *full_name:* string, Descriptive name
        * *categories:* list of strings, Categories of which the variable is a member, listed in hierarchical order
        * *datasources:* url, Retrieves the datasources that define the current variable
        * *url:* url, Endpoint for the observed property variable

    """
    queryset = ObservedPropertyVariable.objects.all()
    serializer_class = ObservedPropertyVariableSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    @action(detail=True)  # Custom Route for an association
    def datasources(self, request, pk=None):
        """
        Retrieve the DataSource Parameters for a broker parameter.

        Maps to  /observed_property_variables/{pk}/datasources/

        :param request:
        :param pk: observed_property_variables primary key
        :return:
        """
        params = DataSourceObservedPropertyVariable.objects.filter(observed_property_variable=pk)
        ds = []
        for dsmv in params:
            ds.append(dsmv.datasource)

        # `HyperlinkedRelatedField` requires the request in the
        # serializer context. Add `context={'request': request}`
        # when instantiating the serializer.

        # Then just serialize and return it!
        serializer = DataSourceSerializer(ds, many=True,
                                          context={'request': request})
        return Response(serializer.data)


class ObservedPropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of available Observation Properties

        **Properties**

        * *observed_property_variable:* string, observed property variable assigned to the observed property
        * *datasource:* string, data source defining the observed property
        * *sampling_medium:* enum, medium in which the observed property is observed
            (WATER, GAS, SOLID_PHASE, OTHER, NOT_APPLICABLE)
        * *description:* string, additional information about the observed property
        * *url:* url, endpoint for observed property

    """
    queryset = ObservedProperty.objects.all()
    serializer_class = ObservedPropertySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
