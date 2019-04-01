"""


`basin3d.synthesis.models.measurement`
**************************************

.. currentmodule:: basin3d.synthesis.models.simulations

:synopsis: Classes to represent Measurements & Results


* :class:`DataPointGroup` - Series of data points grouped by time, space, model, sample  etc.
* :class:`DataPoint` - Base class
* :class:`ImageDataPoint` - Represents any imaging result
* :class:`TimeSeriesDataPoint` - Represents a time series result

---------------------
"""
from collections import namedtuple
from numbers import Number

from basin3d.models import FeatureTypes
from basin3d.plugins import get_datasource_observed_property, \
    get_datasource_observed_property_variable
from basin3d.synthesis.models import Base
from django.utils.datetime_safe import datetime


class TimeValuePair(namedtuple('TimeValuePair', ['timestamp', 'value'])):
    """
    Tuple that represents a time value pair.  This will handle timestamp conversion
    """

    def __new__(cls, timestamp, value):
        # Handle epoch time
        if timestamp:
            timestamp_resolved = None
            if isinstance(timestamp, str) and timestamp.isdigit():
                timestamp_resolved = int(timestamp)
            elif isinstance(timestamp, Number):
                timestamp_resolved = timestamp

            if timestamp_resolved:
                timestamp = datetime.fromtimestamp(timestamp_resolved).isoformat()

        return super().__new__(cls, timestamp, value)


class ResultQuality(object):
    """
    Controlled Vocabulary for result quality
    """
    RESULT_QUALITY_CHECKED = "checked"
    RESULT_QUALITY_UNCHECKED = "unchecked"


class Observation(Base):
    """

    OGC OM_Observation feature type. This is a parent class to which Mixins
        should be added to create observation types with metadata and result.

    Inherited attributes (:class:`Base`):
        - *datasource* (from Base): string

    Attributes:
        - *id:* string,
        - *type:* string,
        - *utc_offset:*, float (offset in hours referenced to UTC), +9
        - *phenomenon_time:* datetime (required OGC attribute timePhenomenon),
        - *observed_property:* string,
        - *feature_of_interest:* string,
        - *feature_of_interest_type:* enum (see FeatureType object)
        - *result_quality:*, string,
        - *geographical_group_id:* string, River system ID (Region ID)
        - *geographical_group_type:* enum (sampling_feature, site, plot, region, point_location, measurement position)
        - *measurement_position:* float, height or depth of observation

    """
    TYPE_MEASUREMENT_TVP_TIMESERIES = "measurement_tvp_timeseries"
    TYPE_MEASUREMENT = "measurement"

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.type = None
        self.utc_offset = None
        self.phenomenon_time = None
        self.observed_property = None
        self.feature_of_interest = None
        self.feature_of_interest_type = None
        # self.geographical_group_id = None  # Delete
        # self.geographical_group_type = None  # Delete
        # self.measurement_position = None  # Delete
        self.result_quality = ResultQuality()

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['feature_of_interest'], **kwargs)
        self.__validate__()

    def __eq__(self, other):
        return self.id == other.id

    def __validate__(self):
        """
        Validate attributes
        """

        # Validate feature of interest type if present is class FeatureTypes
        if self.feature_of_interest_type not in FeatureTypes.TYPES.keys():
            if not isinstance(self.feature_of_interest_type, FeatureTypes):
                raise AttributeError("feature_of_interest_type must be FeatureType")


class TimeMetadataMixin(object):
    """
    Metadata attributes for Observations with a time

    Attributes:
        - *aggregation_duration:* string with controlled vocab (CV follows OGC TM_PeriodDuration)
        - *time_reference_position:* string with controlled vocab (part of OGC interpolationType)
    """
    AGGREGATION_DURATION_YEAR = "year"
    AGGREGATION_DURATION_MONTH = "month"
    AGGREGATION_DURATION_DAY = "day"
    AGGREGATION_DURATION_HOUR = "hour"
    AGGREGATION_DURATION_MINUTE = "minute"
    AGGREGATION_DURATION_SECOND = "second"

    TIME_REFERENCE_START = "start"
    TIME_REFERENCE_MIDDLE = "middle"
    TIME_REFERENCE_END = "end"

    def __init__(self, *args, **kwargs):
        self.aggregation_duration = None
        self.time_reference_position = None

        # Instantiate the serializer superclass
        super(TimeMetadataMixin, self).__init__(*args, **kwargs)


class MeasurementMetadataMixin(object):
    """
    Metadata attributes for Observations type Measurement

    Attributes:
        - *observed_property_variable:* string
        - *statistic:* string with controlled vocab (part of OGC interpolationType)
    """

    STATISTIC_MEAN = "mean"
    STATISTIC_MIN = "min"
    STATISTIC_MAX = "max"
    STATISTIC_TOTAL = "total"

    def __init__(self, *args, **kwargs):
        self.observed_property_variable = None
        self.statistic = None

        # Instantiate the serializer superclass
        super(MeasurementMetadataMixin, self).__init__(*args, **kwargs)


class MeasurementTimeseriesTVPResultMixin(object):
    """
    Result Mixin: Measurement Timeseries TimeValuePair

    Attributes:
        - *result_points:* list of TimeValuePair
        - *unit_of_measurement:* string
    """
    def __init__(self, *args, **kwargs):
        self.result_points = []
        self.unit_of_measurement = None
        self.tvp = TimeValuePair

        # Instantiate the serializer superclass
        super(MeasurementTimeseriesTVPResultMixin, self).__init__(*args, **kwargs)


class MeasurementResultMixin(object):
    """
    Result Mixin: Measurement

    Attibutes:
        - *result_value:* numeric
        - *unit_of_measurement:* string
    """
    def __init__(self, *args, **kwargs):
        self.result_value = None
        self.unit_of_measurement = None

        # Instantiate the serializer superclass
        super(MeasurementResultMixin, self).__init__(*args, **kwargs)


class MeasurementTimeseriesTVPObservation(TimeMetadataMixin, MeasurementMetadataMixin,
                                          MeasurementTimeseriesTVPResultMixin, Observation):
    """
    Series of measurement data points grouped by time (i.e., a timeseries).
    Anything specified at the group level automatically applies to the individual data point.
    Have to call Observation (the one inheriting from Base) last.

    Inherited attributes (:class:`Base`):
        - *datasource* (from Base): string

    Inherited attributes (:class:`Observation`):
        - *id:* string,
        - *type:* string,
        - *utc_offset:*, float (offset in hours referenced to UTC), +9
        - *phenomenon_time:* datetime (required OGC attribute timePhenomenon),
        - *observed_property:* string,
        - *feature_of_interest:* object Feature
        - *result_quality:*, string,

    Inherited attributes (:class:`TimeMetadataMixin`):
        - *aggregation_duration:* string with controlled vocab (CV follows OGC TM_PeriodDuration)
        - *time_reference_position:* string with controlled vocab (part of OGC interpolationType)

    Inherited attributes (:class:`MeasurementMetadataMixin`):
        - *observed_property_variable:* string
        - *statistic:* string with controlled vocab (part of OGC interpolationType)

    Inherited attributes (:class:`MeasurementResultMixin`):
        - *result_points:* list of TimeValuePair
        - *unit_of_measurement:* string

    """
    def __init__(self, datasource, **kwargs):
        kwargs["type"] = self.TYPE_MEASUREMENT_TVP_TIMESERIES

        if "observed_property_variable" in kwargs:

            synth_param = get_datasource_observed_property_variable(
                datasource, kwargs["observed_property_variable"])
            observed_property = get_datasource_observed_property(
                datasource, synth_param.observed_property_variable_id)
            kwargs['observed_property'] = observed_property.id
            kwargs.pop("observed_property_variable")

        # Initialize after the attributes have been set
        super(MeasurementTimeseriesTVPObservation, self).__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id
