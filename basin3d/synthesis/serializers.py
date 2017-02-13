"""
`basin3d.synthesis.models.serializers`
**************************************

.. currentmodule:: basin3d.synthesis.models.serializers

:synopsis: The BASIN-3D Synthesis Model Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>

Serializers that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.

* :class:`IdUrlSerializerMixin` - Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
* :class:`RegionSerializer`
* :class:`ModelSerializer`
* :class:`ModelParameterSerializer`
* :class:`ModelParameterSerializer`
* :class:`MeshSerializer`
* :class:`ModelDomainSerializer`

----------------------------------

"""
from basin3d.models import GeographicalGroup
from basin3d.serializers import MeasurementVariableSerializer
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.simulations import ModelDomain
from rest_framework import serializers
from rest_framework.reverse import reverse


class IdUrlSerializerMixin(object):
    """
    Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the serializer superclass
        super(IdUrlSerializerMixin, self).__init__(*args, **kwargs)

        self.fields["url"] = serializers.SerializerMethodField()

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj: an object instance
        :return: An URL to the current object instance
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-detail'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )


class RegionSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Region`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    geom = serializers.JSONField()
    description = serializers.CharField()
    model_domains = serializers.SerializerMethodField()

    def create(self, validated_data):
        return Region(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance

    def get_model_domains(self, obj):
        """
        Get the Site url based on the current context
        :param obj: ``ModelDomain`` object instance
        :return: An URL to the current object instance
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-model-domains'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )


class ModelSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.simulations.Model`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    version = serializers.CharField()
    dimensionality = serializers.CharField()
    web_location = serializers.URLField()

    def create(self, validated_data):
        return ModelSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.version = validated_data.get('version', instance.version)
        instance.dimensionality = validated_data.get('dimensionality', instance.dimensionality)
        instance.web_location = validated_data.get('web_location', instance.web_location)
        return instance


class ModelParameterSerializer(serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.simulations.ModelParameter`

    """

    id = serializers.CharField()
    model_name = serializers.CharField()
    data_source_name = serializers.CharField()
    value = serializers.FloatField()

    def create(self, validated_data):
        return ModelParameterSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.model_name = validated_data.get('model_name', instance.model_name)
        instance.data_source_name = validated_data.get('data_source_name', instance.data_source_name)
        instance.value = validated_data.get('value', instance.value)
        return instance


class MeshSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.simulations.Mesh`

    """

    url = serializers.SerializerMethodField
    id = serializers.CharField()
    parameters = serializers.ListSerializer(child=ModelParameterSerializer())
    initial_conditions = serializers.ListSerializer(child=MeasurementVariableSerializer())
    geom = serializers.JSONField()

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-detail'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return MeshSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.parameters = validated_data.get('parameters', instance.parameters)
        instance.initial_conditions = validated_data.get('initial_conditions', instance.initial_conditions)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class ModelRunSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.simulations.ModelRun`

    """

    id = serializers.CharField()
    name = serializers.CharField(max_length=50)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    simulation_length = serializers.IntegerField()
    simulation_length_units = serializers.CharField()
    status = serializers.CharField()

    def create(self, validated_data):
        return ModelRunSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.simulation_length = validated_data.get('simulation_length', instance.simulation_length)
        instance.simulation_length_units = validated_data.get('simulation_length_units', instance.simulation_length_units)
        instance.status = validated_data.get('status', instance.status)
        return instance


class ModelDomainSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.simulations.ModelDomain`

    """

    id = serializers.CharField()
    name = serializers.CharField()
    geom = serializers.JSONField()
    url = serializers.SerializerMethodField()
    meshes = serializers.SerializerMethodField()

    def create(self, validated_data):
        return ModelDomain(**validated_data)

    def update(self, instance, validated_data):
        instance.model_domain_id = validated_data.get('id', instance.model_domain_id)
        instance.model_domain_name = validated_data.get('name', instance.model_domain_name)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance

    def get_meshes(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-meshes'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )


class DataPointGroupSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
        Serializes a :class:`basin3d.synthesis.models.measurement.DataPointGroup`

    """

    id = serializers.CharField()
    measurement = serializers.SerializerMethodField()
    geographical_group = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    utc_offset = serializers.IntegerField()
    data_points = serializers.SerializerMethodField()


    def get_measurement(self, obj):
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='measurement-detail',
                           kwargs={'pk': obj.measurement_id},
                           request=self.context["request"], )

    def get_geographical_group(self, obj):

        if obj.geographical_group_type in GeographicalGroup.TYPES.keys():
            if "request" in self.context and self.context["request"]:
                return reverse(viewname='{}-detail'.format(GeographicalGroup.TYPES[obj.geographical_group_type].lower()),
                               kwargs={'pk': obj.geographical_group_id},
                               request=self.context["request"], )

    def get_data_points(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-datapoints'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return DataPointGroupSerializer(**validated_data)


class DataPointSerializer(serializers.Serializer):
    """
        Serializes  :class:`basin3d.synthesis.models.measurement.DataPoint` objects and its
        subclasses.

    """

    # Base attributes
    url = serializers.SerializerMethodField()
    id = serializers.CharField()
    type = serializers.SerializerMethodField()
    measurement = serializers.SerializerMethodField()
    geographical_group = serializers.SerializerMethodField()
    units = serializers.CharField()

    # Time Series
    timestamp = serializers.DateTimeField()
    value = serializers.FloatField()
    temporal_resolution = serializers.CharField()
    reference = serializers.CharField()
    utc_offset = serializers.IntegerField()

    # Image
    size = serializers.FloatField()
    resolution = serializers.FloatField()
    image = serializers.URLField()

    FIELDS_IMAGE = {'size', 'resolution', 'image'}
    FIELDS_TIME_SERIES = {'timestamp','temporal_resolution','reference','utc_offset'}

    def __init__(self, *args, **kwargs):
        """
        Override ``BaseSerializer.__init__`` to modify the fields outputted. This depends on the
        type of :class:`basin3d.synthesis.models.measurement.DataPoint`

        See the synthesis classes for a list of attributes:
            * :class:`basin3d.synthesis.models.measurement.DataPoint`
            * :class:`basin3d.synthesis.models.measurement.ImageDataPoint`
            * :class:`basin3d.synthesis.models.measurement.TimeSeriesDataPoint`


        :param args:
        :param kwargs:
        """
        super(DataPointSerializer,self).__init__(*args, **kwargs)

        field_to_remove = set()
        field_to_remove.update(self.FIELDS_IMAGE)
        field_to_remove.update(self.FIELDS_TIME_SERIES)
        if "instance" in kwargs:
            from basin3d.synthesis.models.measurement import TimeSeriesDataPoint, ImageDataPoint
            if isinstance(kwargs["instance"],TimeSeriesDataPoint):
                field_to_remove -= self.FIELDS_TIME_SERIES
            elif isinstance(kwargs["instance"],ImageDataPoint):
                field_to_remove -= self.FIELDS_IMAGE

        for field in field_to_remove:
            self.fields.pop(field)

    def get_type(self,obj):
        """
        Determine the datapoint Type

        :param obj: ``DataPoint`` object instance
        :return: a string representation of the type
        """
        from basin3d.synthesis.models.measurement import TimeSeriesDataPoint, ImageDataPoint
        if isinstance(obj, TimeSeriesDataPoint):
            return "time_series"
        elif isinstance(obj, ImageDataPoint):
            return "image"
        else:
            return "?"

    def get_measurement(self, obj):
        """
        Resolve the URL to the :class:`basin3d.models.Measurement` object

        :param obj: ``DataPoint`` object instance
        :return: an URL to the :class:`basin3d.models.Measurement` object
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='measurement-detail',
                           kwargs={'pk': obj.measurement_id},
                           request=self.context["request"], )

    def get_geographical_group(self, obj):
        """
       Resolve the URL to the Geographical group

       :param obj: ``DataPoint`` object instance
       :return: an URL to the Geographical group
       """
        if obj.geographical_group_type in GeographicalGroup.TYPES.keys():
            if "request" in self.context and self.context["request"]:
                return reverse(viewname='{}-detail'.format(GeographicalGroup.TYPES[obj.geographical_group_type].lower()),
                               kwargs={'pk': obj.geographical_group_id},
                               request=self.context["request"], )

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj: ``DataPoint`` object instance
        :return: An URL to the current object instance
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='datapoint-detail',
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return DataPointSerializer(**validated_data)
