"""
Broker Model Serializers


Serializers allow complex data such as querysets and model instances to be converted
to native Python datatypes that can then be easily rendered into JSON, XML or other
content types. Serializers also provide deserialization, allowing parsed data to be
converted back into complex types, after first validating the incoming data.
-- http://www.django-rest-framework.org/api-guide/serializers/


"""
from rest_framework import serializers

from basin3d.models import MeasurementVariable, DataSourceMeasurementVariable, DataSource, \
    Measurement
from rest_framework import reverse


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

    Broker parameter Serializer

    """

    class Meta:
        model = MeasurementVariable
        depth = 2


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




