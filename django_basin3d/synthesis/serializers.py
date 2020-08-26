"""
`django_basin3d.synthesis.serializers`
*******************************

.. currentmodule:: django_basin3d.synthesis.serializers

:synopsis: The BASIN-3D Synthesis Model Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>
:module author: Danielle Svehla Christianson <dschristianson@lbl.gov>

Serializers that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.

"""
from numbers import Number

from django.utils.datetime_safe import datetime
from rest_framework import serializers
from rest_framework.reverse import reverse

from django_basin3d.models import FeatureTypes
from django_basin3d.serializers import ChooseFieldsSerializerMixin


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
        super(ReadOnlySynthesisModelField, self).__init__(read_only=True, **kwargs)

    def to_internal_value(self, data):
        raise NotImplementedError

    def to_representation(self, obj):
        serializer = self.serializer_class(obj, context=self.context)
        return serializer.data


class FloatField(serializers.FloatField):
    """
    A Float field that can handle empty strings
    """

    def to_representation(self, value):
        """to float representation"""
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
    """ Serializes a :class:`django_basin3d.synthesis.models.Person`"""

    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    institution = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)


class VerticalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`django_basin3d.synthesis.models.field.VerticalCoordinate` and its child classes """

    value = serializers.FloatField(read_only=True)
    resolution = serializers.FloatField(read_only=True)
    distance_units = serializers.CharField(read_only=True)
    datum = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)


class HorizonatalCoordinateSerializer(serializers.Serializer):
    """ Serializes a :class:`django_basin3d.synthesis.models.field.HorizonatalCoordinate` and its child classes """

    # Base Fields
    x = FloatField(read_only=True)
    y = FloatField(read_only=True)
    datum = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)

    # Geographic Fields
    latitude = FloatField(read_only=True)
    longitude = FloatField(read_only=True)
    units = serializers.CharField(read_only=True)

    # Geographic Fields

    FIELDS_HORIZONTAL = {'X', 'Y'}
    FIELDS_GEOGRAPHIC = {'LATITUDE', 'LONGITUDE'}

    def __init__(self, *args, **kwargs):
        """
        Override ``BaseSerializer.__init__`` to modify the fields outputted. This depends on the
        type of coordinate classes in :class:`django_basin3d.synthesis.field`

        See the synthesis classes for a list of attributes:
            * :class:`django_basin3d.synthesis.models.field.GeographicCoordate`


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

            from basin3d.core.models import GeographicCoordinate
            if isinstance(instance, GeographicCoordinate):
                field_to_remove -= self.FIELDS_GEOGRAPHIC

        # remove unneeded fields
        for field in field_to_remove:
            if field in self.fields:
                self.fields.pop(field)


class AbsoluteCoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.AbsoluteCoordinate`
    """

    horizontal_position = serializers.ListSerializer(
        child=ReadOnlySynthesisModelField(serializer_class=HorizonatalCoordinateSerializer))
    vertical_extent = serializers.ListSerializer(
        child=ReadOnlySynthesisModelField(serializer_class=VerticalCoordinateSerializer))

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RepresentativeCoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.RepresentativeCoordinate`
    """

    representative_point = ReadOnlySynthesisModelField(serializer_class=AbsoluteCoordinateSerializer)
    representative_point_type = serializers.CharField(read_only=True)
    vertical_position = ReadOnlySynthesisModelField(serializer_class=VerticalCoordinateSerializer)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class CoordinateSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.Coordinate`
    """

    absolute = ReadOnlySynthesisModelField(serializer_class=AbsoluteCoordinateSerializer)
    representative = ReadOnlySynthesisModelField(serializer_class=RepresentativeCoordinateSerializer)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RelatedSamplingFeatureSerializer(ChooseFieldsSerializerMixin, IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.RelatedSamplingFeature`
    """
    related_sampling_feature = serializers.CharField(read_only=True)
    related_sampling_feature_type = serializers.SerializerMethodField(read_only=True)
    role = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super(self.__class__, self).__init__(*args, **kwargs)

    # def get_related_sampling_feature(self, obj):
    #     """
    #     Resolve the URL for the feature of interest
    #     :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
    #     :return: an URL to the Monitoring Feature group
    #     """
    #     # ToDo: verify it works without feature_type specified
    #     if "request" in self.context and self.context["request"] and obj.related_sampling_feature:
    #         if obj.related_sampling_feature_type in FeatureTypes.TYPES.keys():
    #             feature_type = FeatureTypes.TYPES[obj.related_sampling_feature_type]
    #             path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
    #         # else:
    #         #     path_route = r'monitoringfeature-detail'
    #             return reverse(viewname=path_route,
    #                            # ToDo: take off the database prefix?
    #                            kwargs={'pk': obj.related_sampling_feature},
    #                            request=self.context["request"], )
    #     return obj.related_sampling_feature

    def get_related_sampling_feature_type(self, obj):
        """
        Convert the :class:`django_basin3d.models.FeatureTypes` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`django_basin3d.models.FeatureTypes` type
        """
        return FeatureTypes.TYPES[obj.related_sampling_feature_type]

    def get_url(self, obj):
        """
        Get the  url based on the current context
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: An URL to the current object instance
        """
        # ToDo: verify it works without feature_type specified
        if "request" in self.context and self.context["request"] and obj.related_sampling_feature:
            if obj.related_sampling_feature_type in FeatureTypes.TYPES.keys():
                feature_type = FeatureTypes.TYPES[obj.related_sampling_feature_type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
                # else:
                #     path_route = r'monitoringfeature-detail'
                try:
                    url = reverse(viewname=path_route,
                                  # ToDo: take off the database prefix?
                                  kwargs={'pk': obj.related_sampling_feature},
                                  request=self.context["request"], )
                except Exception:
                    return None
                return url
        return None


class FeatureSerializer(ChooseFieldsSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.Feature`
    """

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    feature_type = serializers.SerializerMethodField(read_only=True)
    observed_property_variables = serializers.ListField(read_only=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        # ToDo: Figure out what this is doing and explain it better.
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        self.fields["url"] = serializers.SerializerMethodField()

    def get_feature_type(self, obj):
        """
        Convert the :class:`django_basin3d.models.FeatureTypes` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`django_basin3d.models.FeatureTypes` type
        """
        return FeatureTypes.TYPES[obj.feature_type]

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj: an object instance
        :return: An URL to the current object instance
        """
        # ToDo: verify it works without feature_type specified
        if "request" in self.context and self.context["request"]:
            if obj.feature_type is not None:
                feature_type = FeatureTypes.TYPES[obj.feature_type]
                path_route = r'monitoringfeature-{}s-detail'.format(''.join(feature_type.lower().split()))
                # else:
                # path_route = r'monitoringfeature-detail'
                try:
                    url = reverse(viewname=path_route,
                                  # ToDo: take off the database prefix?
                                  kwargs={'pk': obj.id},
                                  request=self.context["request"], )
                except Exception:
                    return None
                return url
        return None


class SamplingFeatureSerializer(FeatureSerializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.SamplingFeature`
    """

    related_sampling_feature_complex = serializers.ListSerializer(
        child=ReadOnlySynthesisModelField(serializer_class=RelatedSamplingFeatureSerializer))

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)


class SpatialSamplingFeatureSerializer(SamplingFeatureSerializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.SpatialSamplingFeature`
    """

    shape = serializers.CharField(read_only=True)
    coordinates = ReadOnlySynthesisModelField(serializer_class=CoordinateSerializer)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)


class MonitoringFeatureSerializer(SpatialSamplingFeatureSerializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.field.MonitoringFeature`
    """
    description_reference = serializers.CharField(read_only=True)
    related_party = serializers.ListSerializer(child=ReadOnlySynthesisModelField(serializer_class=PersonSerializer))
    utc_offset = serializers.IntegerField(read_only=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)


class ObservationSerializerMixin(object):
    """
    Serializes a :class:`django_basin3d.synthesis.models.measurement.Observation`
    """

    def __init__(self, *args, **kwargs):
        super(ObservationSerializerMixin, self).__init__(*args, **kwargs)

        self.fields["id"] = serializers.CharField(read_only=True)
        self.fields["type"] = serializers.CharField(read_only=True)
        self.fields["utc_offset"] = serializers.IntegerField(read_only=True)
        self.fields["phenomenon_time"] = TimestampField(read_only=True)
        self.fields["observed_property_variable"] = serializers.CharField(read_only=True)
        self.fields["result_quality"] = serializers.CharField(read_only=True)
        self.fields["feature_of_interest"] = ReadOnlySynthesisModelField(serializer_class=MonitoringFeatureSerializer)
        self.fields["feature_of_interest_type"] = serializers.SerializerMethodField(read_only=True)

    def get_feature_of_interest_type(self, obj):
        """
        Convert the :class:`django_basin3d.models.FeatureTypes` type to the display value
        :param obj: ``MeasurementTimeseriesTVPObservation`` object instance
        :return: Display value for the :class:`django_basin3d.models.FeatureTypes` type
        """
        return FeatureTypes.TYPES[obj.feature_of_interest_type]


class MeasurementTimeseriesTVPObservationSerializer(ObservationSerializerMixin, serializers.Serializer):
    """
    Serializes a :class:`django_basin3d.synthesis.models.measurement.MeasurementTimeseriesTVPObservation`

    """
    aggregation_duration = serializers.CharField(read_only=True)
    time_reference_position = serializers.CharField(read_only=True)
    statistic = serializers.CharField(read_only=True)
    result_points = serializers.SerializerMethodField()
    unit_of_measurement = serializers.CharField(read_only=True)

    FIELDS_OPTIONAL = {'aggregation_duration', 'time_reference_position', 'statistic'}

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

