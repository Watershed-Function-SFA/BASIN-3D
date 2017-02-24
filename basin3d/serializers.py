"""
`basin3d.serializers`
*********************

.. currentmodule:: basin3d.serializers

:platform: Unix, Mac
:synopsis: BASIN-3D Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

About Django Serializers:

    Serializers allow complex data such as querysets and model instances to be converted
    to native Python datatypes that can then be easily rendered into JSON, XML or other
    content types. Serializers also provide deserialization, allowing parsed data to be
    converted back into complex types, after first validating the incoming data.
    *-- http://www.django-rest-framework.org/api-guide/serializers/*


"""
from basin3d.models import MeasurementVariable, DataSourceMeasurementVariable, DataSource, \
    Measurement
from rest_framework import reverse
from rest_framework import serializers


class DelimitedListField(serializers.ListField):
    """
    Convert a delemited string field to a list
    """

    child = serializers.CharField()

    def __init__(self, *args, delimiter=",", **kwargs):
        super(DelimitedListField, self).__init__(*args, **kwargs)
        self.delimiter = delimiter

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        data_values = data.split(self.delimiter)
        return [self.child.to_representation(item) if item is not None else None for item in
                data_values]


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    """

    Data Source serializer that converts a models.DataSource

    """

    direct_path = serializers.SerializerMethodField()

    def get_direct_path(self, obj ):
        """
        Return the url for direct api access
        :param obj:
        :return:
        """
        format = None
        if "format" in self.context["request"].query_params:
            format = self.context["request"].query_params["format"]
        url_kwargs = {
            'id_prefix': obj.id_prefix,
            'direct_path':''
        }
        return reverse.reverse('direct-path-detail', kwargs=url_kwargs,
                               request=self.context["request"], format=format)

    class Meta:
        model = DataSource
        depth=1
        fields = ('url', 'direct_path','name', 'location','id_prefix')
        read_only_fields = ('name', 'location', 'id_prefix')
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

    Measurement Variable serializer

    """

    categories = DelimitedListField()

    class Meta:
        model = MeasurementVariable
        depth = 2
        fields = ('url', 'id', 'full_name', 'categories')


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    """

    Broker parameter Serializer

    """

    sampling_medium = serializers.SerializerMethodField()
    measurement_approach = serializers.SerializerMethodField()

    def get_sampling_medium(self, obj):
        return obj.sampling_medium.name

    def get_measurement_approach(self, obj):
        return obj.measurement_approach.name

    class Meta:
        model = Measurement
        depth = 2




