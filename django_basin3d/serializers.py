"""
`django_basin3d.serializers`
*********************

.. currentmodule:: django_basin3d.serializers

:platform: Unix, Mac
:synopsis: BASIN-3D Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

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
from django_basin3d.models import DataSource, ObservedProperty, ObservedPropertyVariable, \
    DataSourceObservedPropertyVariable
from rest_framework import reverse
from rest_framework import serializers


class ChooseFieldsSerializerMixin(object):
    """
    A serializer that  dynamically sets fields
    """

    def __init__(self, *args, **kwargs):

        # Instantiate the serializer superclass
        super(ChooseFieldsSerializerMixin, self).__init__(*args, **kwargs)

        if 'request' in self.context:
            self.handle_fields(self.context['request'])

    def handle_fields(self, request=None):
        """
        Restrict the fields by those in the request
        :param request:
        :return:
        """
        if request:
            fields = request.query_params.get('fields')
            if fields and len(fields) > 0:
                field_set = set(fields.split(","))

                # Remove the fields not in the intersection
                for field in set(self.fields.keys()).difference(field_set):
                    self.fields.pop(field)


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

    observed_property_variables = serializers.SerializerMethodField()
    check = serializers.SerializerMethodField()

    def get_observed_property_variables(self, obj):
        """
        Return the url for the observed property variables associated with the current datasource
        :param obj:
        :return:
        """
        format = None
        if "format" in self.context["request"].query_params:
            format = self.context["request"].query_params["format"]
        url_kwargs = {
            "pk": obj.id,
        }
        return reverse.reverse("{}-observed-property-variables".format(obj.__class__.__name__.lower()),
                               kwargs=url_kwargs,
                               request=self.context["request"], format=format)

    def get_check(self, obj):
        """
        Check the data source
        :param obj:
        :return:
        """
        url_kwargs = {
            'pk': obj.id,
        }
        return "{}check/".format(reverse.reverse('datasource-detail', kwargs=url_kwargs,
                                                 request=self.context["request"], ))

    class Meta:
        model = DataSource
        depth = 1
        fields = ('url', 'name', 'location', 'id_prefix',
                  'observed_property_variables', 'check')
        read_only_fields = ('name', 'location', 'id_prefix',
                            'observed_property_variables', 'check')
        lookup_field = 'name'


class DataSourceObservedPropertyVariableSerializer(serializers.HyperlinkedModelSerializer):
    """
    Model that Serializes Mapped Data Source Parameters

    """

    class Meta:
        model = DataSourceObservedPropertyVariable
        fields = ('id', 'name', 'datasource', 'observed_property_variable')


class ObservedPropertyVariableSerializer(serializers.HyperlinkedModelSerializer):
    """
    Observed Property Variable Serializer

    """

    categories = DelimitedListField()
    datasources = serializers.SerializerMethodField()

    def get_datasources(self, obj):
        """
        Return the url for the data sources associated with the current variable
        :param obj:
        :return:
        """
        format = None
        if "format" in self.context["request"].query_params:
            format = self.context["request"].query_params["format"]
        url_kwargs = {
            "pk": obj.basin3d_id,
        }
        return reverse.reverse("{}-datasources".format(obj.__class__.__name__.lower()), kwargs=url_kwargs,
                               request=self.context["request"], format=format)

    class Meta:
        model = ObservedPropertyVariable
        depth = 2
        fields = ('url', 'basin3d_id', 'full_name', 'categories', 'datasources')


class ObservedPropertySerializer(serializers.HyperlinkedModelSerializer):
    """
    Observed Property Serializer

    """

    sampling_medium = serializers.SerializerMethodField()
    datasource = serializers.SerializerMethodField()
    observed_property_variable = serializers.SerializerMethodField()

    def get_sampling_medium(self, obj):
        return obj.sampling_medium.name

    def get_datasource(self, obj):
        return obj.datasource.name

    def get_observed_property_variable(self, obj):
        return obj.observed_property_variable.basin3d_id

    class Meta:
        model = ObservedProperty
        depth = 2
        fields = '__all__'
