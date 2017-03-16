"""
`basin3d.synthesis.serializers`
*******************************

.. currentmodule:: basin3d.synthesis.serializers

:synopsis: The BASIN-3D Synthesis Model Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>

Serializers that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.


* :class:`DataPointGroupSerializer`
* :class:`DataPointSerializer`
* :class:`FloatField` -  A Float field that can handle empty strings
* :class:`HorizontalCoordinateSerializer`
* :class:`IdUrlSerializerMixin` - Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
* :class:`MeasurementPositionSerializer`
* :class:`MeshSerializer`
* :class:`ModelDomainSerializer`
* :class:`ModelParameterSerializer`
* :class:`ModelRunSerializer`
* :class:`ModelSerializer`
* :class:`ModelParameterSerializer`
* :class:`PersonSerializer`
* :class:`PlotSerializer`
* :class:`PointLocationSerializer`
* :class:`ReadOnlySynthesisModelField` -  A generic field that can be used against any serializer
* :class:`RegionSerializer`
* :class:`SiteSerializer`
* :class:`TimestampSerializer` - Extends :class:`rest_framework.serializers.DateTimeField` to handle
    numeric epoch times.

"""
from numbers import Number

from basin3d.models import GeographicalGroup
from basin3d.serializers import MeasurementVariableSerializer, MeasurementSerializer
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.simulations import ModelDomain
from django.utils.datetime_safe import datetime
from rest_framework import serializers
from rest_framework.reverse import reverse


class TimestampField(serializers.DateTimeField):
    """
    Extends :class:`rest_framework.serializers.DateTimeField` to handle
    numeric epoch times.

    """

    def to_representation(self, value):
        """
        If specified value is an epoch time, convert it first.

        :param value:
        :return:
        """

        # Handle epoch time
        timestamp = None
        if isinstance(value, str) and value.isdigit():
            timestamp = int(value)
        elif isinstance(value, Number):
            timestamp = value

        if timestamp:
            value = datetime.fromtimestamp(timestamp).strftime('%m/%d/%y %H:%M:%S.%f')

        return super(TimestampField, self).to_representation(value)


class ReadOnlySynthesisModelField(serializers.Field):
    """
    A generic field that can be used against any serializer
    """

    def __init__(self, serializer_class, **kwargs):
        self.serializer_class = serializer_class
        super(ReadOnlySynthesisModelField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        raise NotImplemented

    def to_representation(self, obj):
        serializer = self.serializer_class(obj, context=self.context)
        return serializer.data


class FloatField(serializers.FloatField):
    """
    A Float field that can handle empty strings
    """

    def to_representation(self, value):
        if not value:
            return None
        return float(value)


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


class PersonSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.Person`"""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    institution = serializers.CharField()

    def create(self, validated_data):
        return PersonSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.institution = validated_data.get('institution', instance.institution)


class VerticalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.field.VerticalCoordinate` and its base classes """

    value = serializers.FloatField()
    resolution = serializers.FloatField()
    distance_units = serializers.CharField()
    encoding_method = serializers.CharField
    datum = serializers.CharField()
    type = serializers.CharField()


class HorizonatalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.field.HorizonatalCoordinate` and its base classes """

    # Base Fields
    x = FloatField()
    y = FloatField()
    datum = serializers.CharField()
    type = serializers.CharField()

    # Geographic Fields
    latitude = FloatField()
    longitude = FloatField()
    units = serializers.CharField()

    # Geographic Fields

    FIELDS_HORIZONTAL = {'x', 'y'}
    FIELDS_GEOGRAPHIC = {'latitude', 'longitude'}

    def __init__(self, *args, **kwargs):
        """
        Override ``BaseSerializer.__init__`` to modify the fields outputted. This depends on the
        type of coordinate classes in :class:`basin3d.synthesis.field`

        See the synthesis classes for a list of attributes:
            * :class:`basin3d.synthesis.models.field.GeographicCoordate`


        :param args:
        :param kwargs:
        """
        super(HorizonatalCoordinateSerializer, self).__init__(*args, **kwargs)

        field_to_remove = set()
        field_to_remove.update(self.FIELDS_HORIZONTAL)
        field_to_remove.update(self.FIELDS_GEOGRAPHIC)
        instance = None
        if "instance" in kwargs:
            instance = kwargs["instance"]
        elif len(args) >= 1:
            if args[0] and isinstance(args[0], (list, tuple)) and not isinstance(args[0], str):
                instance = args[0][0]
            else:
                instance = args[0]

        if instance:

            from basin3d.synthesis.models.field import GeographicCoordinate
            if isinstance(instance, GeographicCoordinate):
                field_to_remove -= self.FIELDS_GEOGRAPHIC

        # remove unneeded fields
        for field in field_to_remove:
            self.fields.pop(field)


class SiteSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Site`
    """

    def __init__(self, *args, **kwargs):
        """
        Override ``BaseSerializer.__init__`` to modify the fields outputted. Remove ```geom```
        if it is not being used


        :param args:
        :param kwargs:
        """
        super(SiteSerializer, self).__init__(*args, **kwargs)

        instance = None
        if "instance" in kwargs:
            instance = kwargs["instance"]
        elif len(args) >= 1:
            if args[0] and isinstance(args[0], (list, tuple)) and not isinstance(args[0], str):
                instance = args[0][0]
            else:
                instance = args[0]

        if instance and not instance.geom:
            self.fields.pop("geom")

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    country = serializers.CharField()
    state_province = serializers.CharField()
    utc_offset = serializers.IntegerField()
    center_coordinates = ReadOnlySynthesisModelField(
        serializer_class=HorizonatalCoordinateSerializer)
    geom = serializers.JSONField()
    contacts = serializers.ListSerializer(child=ReadOnlySynthesisModelField(PersonSerializer))
    pi = ReadOnlySynthesisModelField(serializer_class=PersonSerializer)
    urls = serializers.ListSerializer(child=serializers.URLField())

    def create(self, validated_data):
        return SiteSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.country = validated_data.get('country', instance.country)
        instance.state_province = validated_data.get('state_province', instance.state_province)
        instance.center_coordinates = validated_data.get('center_coordinates',
                                                         instance.center_coordinates)
        instance.geom = validated_data.get('geom', instance.geom)
        instance.contacts = validated_data.get('contacts', instance.contacts)
        instance.pi = validated_data.get('pi', instance.pi)
        instance.urls = validated_data.get('urls', instance.urls)
        instance.type = validated_data.get('type', instance.type)

        return instance


class PlotSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Plot`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    site = serializers.SerializerMethodField()
    geom = serializers.JSONField()
    pi = ReadOnlySynthesisModelField(serializer_class=PersonSerializer)

    def get_site(self, obj):
        """
        Get the site url
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='site-detail',
                           kwargs={'pk': obj.site_id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return PlotSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geom = validated_data.get('geom', instance.geom)
        instance.pi = validated_data.get('pi', instance.pi)
        instance.type = validated_data.get('type', instance.type)
        instance.site_id = validated_data.get('site_id', instance.site_id)

        return instance


class PointLocationSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.PointLocation`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    site = serializers.SerializerMethodField()
    geographical_group = serializers.SerializerMethodField()
    geographical_group_type = serializers.SerializerMethodField()
    horizontal_position = ReadOnlySynthesisModelField(
        serializer_class=HorizonatalCoordinateSerializer)

    def get_geographical_group_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``DataPoint`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return GeographicalGroup.TYPES[obj.geographical_group_type]

    def get_geographical_group(self, obj):
        """
        Resolve the URL to the Geographical group

        :param obj: ``DataPoint`` object instance
        :return: an URL to the Geographical group
        """

        if obj.geographical_group_type in GeographicalGroup.TYPES.keys():
            if "request" in self.context and self.context["request"]:
                return reverse(viewname='{}-detail'.format(
                    GeographicalGroup.TYPES[obj.geographical_group_type].lower()),
                               kwargs={'pk': obj.geographical_group_id},
                               request=self.context["request"], )

    def get_site(self, obj):
        """
        Get the site url
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='site-detail',
                           kwargs={'pk': obj.site_id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return PointLocationSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geographical_group = validated_data.get('geographical_group',
                                                         instance.geographical_group)
        instance.type = validated_data.get('type', instance.type)
        instance.site_id = validated_data.get('site_id', instance.site_id)
        instance.horizontal_position = validated_data.get('horizontal_position',
                                                          instance.horizontal_position)

        return instance


class MeasurementPositionSerializer(serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.MeasurementPosition`
    """

    type = serializers.CharField()
    point_location = serializers.SerializerMethodField()
    vertical_position = ReadOnlySynthesisModelField(
        serializer_class=VerticalCoordinateSerializer)

    def get_point_location(self, obj):
        """
        Get the site url
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='pointlocation-detail',
                           kwargs={'pk': obj.point_location_id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return MeasurementPositionSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.point_location_id = validated_data.get('point_location_id', instance.depth_height)
        instance.vertical_position = validated_data.get('vertical_position',
                                                         instance.depth_height_units)

        return instance


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
    geographical_group_type = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    utc_offset = serializers.IntegerField()
    data_points = serializers.SerializerMethodField()

    def get_measurement(self, obj):
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='measurement-detail',
                           kwargs={'pk': obj.measurement_id},
                           request=self.context["request"], )

    def get_geographical_group_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``DataPoint`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return GeographicalGroup.TYPES[obj.geographical_group_type]

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
    geographical_group = serializers.SerializerMethodField()
    geographical_group_type = serializers.SerializerMethodField()
    units = serializers.CharField()
    measurement_position = ReadOnlySynthesisModelField(
        serializer_class=MeasurementPositionSerializer)
    measurement = ReadOnlySynthesisModelField(serializer_class=MeasurementSerializer)

    # Time Series
    timestamp = TimestampField()
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
        instance = None
        if "instance" in kwargs:
            instance = kwargs["instance"]
        elif len(args) >= 1:
            if args[0] and isinstance(args[0], (list, tuple)) and not isinstance(args[0], str):
                instance = args[0][0]
            else:
                instance = args[0]

        if instance:

            from basin3d.synthesis.models.measurement import TimeSeriesDataPoint, ImageDataPoint
            if isinstance(instance, TimeSeriesDataPoint):
                field_to_remove -= self.FIELDS_TIME_SERIES
                if not hasattr(instance, "measurement_position"):
                    field_to_remove.update(("measurement_position",))
            elif isinstance(instance, ImageDataPoint):
                field_to_remove -= self.FIELDS_IMAGE

            # Remove optional fields.  We don't want them crowding
            # the json
            if not instance.id:
                field_to_remove.update(["id", "url"])

        # remove unneeded fields
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


    def get_geographical_group_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``DataPoint`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return GeographicalGroup.TYPES[obj.geographical_group_type]

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
