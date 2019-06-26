"""
`basin3d.viewsets`
******************

.. currentmodule:: basin3d.viewsets

:platform: Unix, Mac
:synopsis: BASIN-3D ViewSets
:module author: Val Hendrix <vhendrix@lbl.gov>, Danielle Svehla Christianson <dschristianson@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

* :class:`DirectAPIViewSet` - supports REST ` `GET`` methods that list the direct datasource APIs
* :class:`DataSourceViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.synthesis.models.DataSource` objects
* :class:`ObservedPropertyVariableViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.models.ObservedPropertyVariable` objects
* :class:`ObservedPropertyViewSet` - supports REST ` `GET`` methods that synthesize :class:`~basin3d.models.ObservedProperty` objects

"""
import json
import logging

import django_filters
from basin3d import get_url
from basin3d.models import DataSource, ObservedProperty, ObservedPropertyVariable, \
    DataSourceObservedPropertyVariable
from basin3d.serializers import DataSourceSerializer, \
    ObservedPropertySerializer, ObservedPropertyVariableSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)


class DirectAPIViewSet(viewsets.GenericViewSet):
    """
    Direct Access to data source APIs
    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    lookup_field = 'id_prefix'

    def list(self, request, *args, **kwargs):
        """
        Build the list of Direct APIs that can be accessed

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        direct_apis = []
        for datasource in self.queryset:
            direct_apis.append(
                {datasource.name: request.build_absolute_uri(reverse('direct-path-detail',
                                                                     kwargs={
                                                                         "id_prefix": datasource.id_prefix,
                                                                         "direct_path": ""}))})

        return Response(direct_apis)

    def retrieve(self, request, *args, **kwargs):
        """ direct call to API"""

        datasource = self.get_object()

        if datasource.enabled:
            direct_path = ""
            if "direct_path" in kwargs.keys():
                direct_path = kwargs["direct_path"]

            plugin = datasource.get_plugin()
            response = plugin.direct(request, direct_path)
            if response:
                try:
                    return Response(
                        data=json.loads(
                            response.content.decode('utf-8').replace(datasource.location,
                                                                     request.build_absolute_uri(
                                                                         reverse('direct-path-detail',
                                                                                 kwargs={
                                                                                     "id_prefix": datasource.id_prefix,
                                                                                     "direct_path": ""})))),
                        status=response.status_code)
                except Exception:
                    return response

        return Response(status=status.HTTP_404_NOT_FOUND)


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Returns a list of all Data Sources available to the BASIN-3D service

        ** Properties **

        * *name:* string, Unique name for the Data Source
        * *id_prefix:* string, unique id prefix for all Data Source ids
        * *location:* string, Location of the Data Source
        * *url:* url, Endpoint for Data Source
        * *direct_path:* url, A direct call to the data source itself
        * *observed_property_variables:* url, Observed property variables for Data Source
        * *check:* url, Validate the Data Source connection

    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

    @detail_route()
    def check(self, request, pk=None):
        """
        Determine if Datasource is available
        :param request:
        :param pk:
        :return:
        """

        datasource = self.get_object()
        if datasource.enabled:
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

    @detail_route()  # Custom Route for an association
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

    @detail_route()  # Custom Route for an association
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
