"""
Broker Model Serializers


Serializers allow complex data such as querysets and model instances to be converted
to native Python datatypes that can then be easily rendered into JSON, XML or other
content types. Serializers also provide deserialization, allowing parsed data to be
converted back into complex types, after first validating the incoming data.
-- http://www.django-rest-framework.org/api-guide/serializers/


"""
from rest_framework import serializers

from basin3d.models import MeasurementVariable, DataSourceMeasurementVariable, DataSource


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    """

    Data Source serializer that converts a models.DataSource

    """
    class Meta:
        model = DataSource
        depth=1
        fields = ('url', 'name', 'location')
        read_only_fields = ('name', 'location',)
        lookup_field = 'name'


class DataSourceMeasurementVariableSerializer(serializers.HyperlinkedModelSerializer):
    """
    Model that Serializes Mapped Data Source Parameters

    """
    class Meta:
        model = DataSourceMeasurementVariable
        fields = ('id', 'name', 'datasource', 'measure_variable')


class MeasurementVariableSerializer(serializers.HyperlinkedModelSerializer):
    """

    Broker parameter Serializer

    """

    class Meta:
        model = MeasurementVariable
        depth = 2




