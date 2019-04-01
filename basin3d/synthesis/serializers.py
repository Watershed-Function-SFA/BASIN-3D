"""
`basin3d.synthesis.serializers`
*******************************

.. currentmodule:: basin3d.synthesis.serializers

:synopsis: The BASIN-3D Synthesis Model Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>

Serializers that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.


* :class:`FloatField` -  A Float field that can handle empty strings
* :class:`HorizontalCoordinateSerializer`
* :class:`IdUrlSerializerMixin` - Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
* :class:`MeasurementPositionSerializer`
* :class:`PersonSerializer`
* :class:`PlotSerializer`
* :class:`PointLocationSerializer`
* :class:`ReadOnlySynthesisModelField` -  A generic field that can be used against any serializer
* :class:`RegionSerializer`
* :class:`SiteSerializer`
* :class:`TimestampSerializer` - Extends :class:`rest_framework.serializers.DateTimeField` to handle
    numeric epoch times.
* :class:`ObservationSerializerMixin`
* :class:`MeasurementTimeseriesTVPObservationSerializer`

"""
from numbers import Number

from basin3d.models import GeographicalGroup, FeatureTypes, get_feature_types
from basin3d.serializers import ChooseFieldsSerializerMixin
from basin3d.synthesis.models.field import Region
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

        # ToDo: add additional time formats
        if timestamp:
            value = datetime.fromtimestamp(timestamp).isoformat()

        return value


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


class PersonSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.Person`"""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    institution = serializers.CharField()
    role = serializers.CharField()

    def create(self, validated_data):
        return PersonSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.institution = validated_data.get('institution', instance.institution)
        instance.role = validated_data.get('role', instance.role)


class VerticalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.field.VerticalCoordinate` and its child classes """

    value = serializers.FloatField()
    resolution = serializers.FloatField()
    distance_units = serializers.CharField()
    encoding_method = serializers.CharField
    datum = serializers.CharField()
    type = serializers.CharField()


class HorizonatalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`basin3d.synthesis.models.field.HorizonatalCoordinate` and its child classes """

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
            if field in self.fields:
                self.fields.pop(field)


class AbsoluteCoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.AbsoluteCoordinate`
    """

    horizontal_position = serializers.ListSerializer(child=ReadOnlySynthesisModelField(serializer_class=HorizonatalCoordinateSerializer))
    vertical_extent = serializers.ListSerializer(child=ReadOnlySynthesisModelField(serializer_class=VerticalCoordinateSerializer))

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RepresentativeCoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.RepresentativeCoordinate`
    """

    representative_point = ReadOnlySynthesisModelField(serializer_class=AbsoluteCoordinateSerializer)
    representative_point_type = serializers.CharField()
    vertical_position = ReadOnlySynthesisModelField(serializer_class=VerticalCoordinateSerializer)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class CoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Coordinate`
    """

    absolute = ReadOnlySynthesisModelField(serializer_class=AbsoluteCoordinateSerializer)
    representative = ReadOnlySynthesisModelField(serializer_class=RepresentativeCoordinateSerializer)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RelatedSamplingFeatureSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
    """

    """
    related_sampling_feature = serializers.SerializerMethodField()
    related_sampling_feature_type = serializers.SerializerMethodField()
    role = serializers.CharField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super(self.__class__, self).__init__(*args, **kwargs)

    def get_related_sampling_feature(self, obj):
        """
        Resolve the URL for the feature of interest
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: an URL to the Monitoring Feature group
        """
        """
        path_route = None
        # ToDo: refactor to use get_feature_types (synthesis.models)
        # ToDo: work without type specified
        if "request" in self.context and self.context["request"] and obj.related_sampling_feature is not None:
            for key, feature_type in FeatureTypes.TYPES.items():
                if key == obj.related_sampling_feature_type:
                    ft = ''.join(feature_type.lower().split())
                    path_route = r'monitoringfeature-{}s-detail'.format(ft)
            if path_route is not None:
                return reverse(
                    viewname=path_route,
                    # ToDo: take off the database prefix?
                    kwargs={'pk': obj.related_sampling_feature},
                    request=self.context["request"], )

        return obj.related_sampling_feature
        """
        if "request" in self.context and self.context["request"] and obj.related_sampling_feature:
            if not obj.related_sampling_feature_type:
                feature_type = FeatureTypes.TYPES[obj.related_sampling_feature_type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
            else:
                path_route = r'monitoringfeature-detail'
            return reverse(viewname=path_route,
                           # ToDo: take off the database prefix?
                           kwargs={'pk': obj.related_sampling_feature},
                           request=self.context["request"], )
        return obj.related_sampling_feature

    def get_related_sampling_feature_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return FeatureTypes.TYPES[obj.related_sampling_feature_type]

    def get_url(self, obj):
        """
        Get the  url based on the current context
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: An URL to the current object instance
        """
        """
        path_route = None
        # ToDo: refactor to use get_feature_types (synthesis.models)
        # ToDo: work without type specified
        if obj.related_sampling_feature is not None and "request" in self.context and self.context["request"]:
            for key, feature_type in FeatureTypes.TYPES.items():
                if key == obj.related_sampling_feature_type:
                    ft = ''.join(feature_type.lower().split())
                    path_route = r'monitoringfeature-{}s-detail'.format(ft)
            if path_route is not None:
                return reverse(viewname=path_route,
                               kwargs={'pk': obj.related_sampling_feature},
                               request=self.context["request"], )
        return None
        """
        if "request" in self.context and self.context["request"] and obj.related_sampling_feature:
            if obj.related_sampling_feature_type:
                feature_type = FeatureTypes.TYPES[obj.related_sampling_feature_type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
            else:
                path_route = r'monitoringfeature-detail'
            return reverse(viewname=path_route,
                           # ToDo: take off the database prefix?
                           kwargs={'pk': obj.related_sampling_feature},
                           request=self.context["request"], )
        return None


class FeatureSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Feature`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.SerializerMethodField()
    observed_property_variables = serializers.ListField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        # ToDo: Figure out what this is doing and explain it better.
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        self.fields["url"] = serializers.SerializerMethodField()

    def get_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return FeatureTypes.TYPES[obj.type]

    def create(self, validated_data):
        return FeatureSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        return instance

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj: an object instance
        :return: An URL to the current object instance
        """
        """
        path_route = None
        # ToDo: refactor to use get_feature_types (synthesis.models)
        # ToDo: work without type specified
        if "request" in self.context and self.context["request"] and obj.type is not None:
            for key, feature_type in FeatureTypes.TYPES.items():
                if key == obj.type:
                    ft = ''.join(feature_type.lower().split())
                    path_route = r'monitoringfeature-{}s-detail'.format(ft)
            if path_route is not None:
                return reverse(viewname=path_route,
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-detail'.format(
                obj.__class__.__name__.lower()),
                kwargs={'pk': obj.id},
                request=self.context["request"], )
        return None
        """
        if "request" in self.context and self.context["request"]:
            if obj.type is not None:
                feature_type = FeatureTypes.TYPES[obj.type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
            else:
                path_route = r'monitoringfeature-detail'
            return reverse(viewname=path_route,
                           # ToDo: take off the database prefix?
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )
        return None


class SamplingFeatureSerializer(FeatureSerializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.SamplingFeature`
    """

    related_sampling_feature_complex = serializers.ListSerializer(
        child=ReadOnlySynthesisModelField(serializer_class=RelatedSamplingFeatureSerializer))

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return SamplingFeatureSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.related_sampling_feature_complex = validated_data.get(
            'related_sampling_feature_complex', instance.related_sampling_feature_complex)


class SpatialSamplingFeatureSerializer(SamplingFeatureSerializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.SpatialSamplingFeature`
    """

    shape = serializers.CharField()
    coordinates = ReadOnlySynthesisModelField(serializer_class=CoordinateSerializer)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return SpatialSamplingFeatureSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.shape = validated_data.get('shape', instance.shape)
        instance.coordinates = validated_data.get('coordinates', instance.coordinates)


class MonitoringFeatureSerializer(SpatialSamplingFeatureSerializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.MonitoringFeature`
    """
    description_reference = serializers.CharField()
    related_party = serializers.ListSerializer(child=ReadOnlySynthesisModelField(serializer_class=PersonSerializer))
    utc_offset = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return MonitoringFeatureSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.description_reference = validated_data.get('description_reference', instance.description_reference)
        instance.related_party = validated_data.get('related_party', instance.related_party)
        instance.utc_offset = validated_data.get('utc_offset', instance.utc_offset)


class RegionSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.field.Region`
    """

    id = serializers.CharField()
    name = serializers.CharField()
    geom = serializers.JSONField()
    description = serializers.CharField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(self.__class__, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        return Region(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class SiteSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
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
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)

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
            if "geom" in self.fields:
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


class PlotSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
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

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(self.__class__, self).__init__(*args, **kwargs)

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


class PointLocationSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
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
    vertical_extent = ReadOnlySynthesisModelField(
        serializer_class=VerticalCoordinateSerializer)
    observed_property_variables = serializers.ListField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(self.__class__, self).__init__(*args, **kwargs)

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


class ObservationSerializerMixin(object):
    """
    Serializes a :class:`basin3d.synthesis.models.measurement.Observation`
    """
    def __init__(self, *args, **kwargs):
        super(ObservationSerializerMixin, self).__init__(*args, **kwargs)

        self.fields["id"] = serializers.CharField()
        self.fields["type"] = serializers.CharField()
        self.fields["utc_offset"] = serializers.IntegerField()
        self.fields["phenomenon_time"] = TimestampField()
        self.fields["observed_property"] = serializers.SerializerMethodField()
        self.fields["result_quality"] = serializers.CharField()
        self.fields["feature_of_interest"] = serializers.SerializerMethodField()
        self.fields["feature_of_interest_type"] = serializers.SerializerMethodField()
        # self.fields["geographical_group_id"] = serializers.SerializerMethodField()  # Delete
        # self.fields["geographical_group_type"] = serializers.SerializerMethodField()  # Delete
        # self.fields["measurement_position"] = ReadOnlySynthesisModelField(
            # serializer_class=MeasurementPositionSerializer)  # Delete

    def get_observed_property(self, obj):
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='observedproperty-detail',
                           kwargs={'pk': obj.observed_property},
                           request=self.context["request"], )
        else:
            return obj.observed_property

    def get_feature_of_interest(self, obj):
        """
        Resolve the URL for the feature of interest
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: an URL to the Monitoring Feature group
        """
        """
        if "request" in self.context and self.context["request"]:
            return reverse(
                # ToDo: fix this url
                viewname='monitoring_features/{}-detail'.format(FeatureTypes.TYPES[obj.feature_of_interest_type].lower()),
                kwargs={'pk': obj.id},
                request=self.context["request"], )
        else:
            return obj.feature_of_interest
        """
        if "request" in self.context and self.context["request"] and obj.feature_of_interest:
            if obj.feature_of_interest_type:
                feature_type = FeatureTypes.TYPES[obj.feature_of_interest_type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
            else:
                path_route = r'monitoringfeature-detail'
            return reverse(viewname=path_route,
                           # ToDo: take off the database prefix?
                           kwargs={'pk': obj.feature_of_interest},
                           request=self.context["request"], )
        return obj.feature_of_interest

    def get_feature_of_interest_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return FeatureTypes.TYPES[obj.feature_of_interest_type]

    # Delete
    def get_geographical_group_type(self, obj):
        """
        Convert the :class:`basin3d.models.GeographicalGroup` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`basin3d.models.GeographicalGroup` type
        """
        return GeographicalGroup.TYPES[obj.geographical_group_type]

    # Delete
    def get_geographical_group_id(self, obj):
        """
        Resolve the URL to the Geographical group

        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: an URL to the Geographical group
        """

        if obj.geographical_group_type in GeographicalGroup.TYPES.keys():
            if "request" in self.context and self.context["request"]:
                return reverse(
                    viewname='{}-detail'.format(GeographicalGroup.TYPES[obj.geographical_group_type].lower()),
                    kwargs={'pk': obj.geographical_group_id},
                    request=self.context["request"], )
            else:
                return obj.geographical_group_id


class MeasurementTimeseriesTVPObservationSerializer(ObservationSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`basin3d.synthesis.models.measurement.MeasurementTimeseriesTVPObservation`

    """
    aggregation_duration = serializers.CharField()
    time_reference_position = serializers.CharField()
    statistic = serializers.CharField()
    result_points = serializers.SerializerMethodField()
    unit_of_measurement = serializers.CharField()

    FIELDS_OPTIONAL = {'aggregation_duration', 'time_reference_position', 'utc_offset', 'statistic'}

    def __init__(self, *args, **kwargs):
        """
        Override ``BaseSerializer.__init__`` to modify the fields outputted. Remove id if it doesn't exist

        :param args:
        :param kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)

        super(MeasurementTimeseriesTVPObservationSerializer, self).__init__(*args, **kwargs)

        field_to_remove = set()

        instance = None
        if "instance" in kwargs:
            instance = kwargs["instance"]
        elif len(args) >= 1:
            if args[0] and isinstance(args[0], (list, tuple)) and not isinstance(args[0], str):
                instance = args[0][0]
            else:
                instance = args[0]

        if instance:
            # Remove optional fields.  We don't want them crowding the json
            if not instance.id:
                field_to_remove.update(["id", "url"])
            for field in self.FIELDS_OPTIONAL:
                if not instance.__getattribute__(field):
                    field_to_remove.update([field])

        # remove unneeded fields
        for field in field_to_remove:
            if field in self.fields:
                self.fields.pop(field)

    def get_result_points(self, obj):
        """
        Get the result points (i.e., the timeseries data)
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return:
        """
        return obj.result_points

    def get_url(self, obj):
        """
        Get the  url based on the current context
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: An URL to the current object instance
        """
        if obj.id and "request" in self.context and self.context["request"]:
            return reverse(viewname='measurementtvptimeseries-detail',
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )

    def create(self, validated_data):
        return MeasurementTimeseriesTVPObservationSerializer(**validated_data)
