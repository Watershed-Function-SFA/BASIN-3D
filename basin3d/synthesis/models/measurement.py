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

from basin3d.plugins import get_datasource_observed_property, \
    get_datasource_observed_property_variable, get_datasource_variable, get_datasource_measurement
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
        self.geographical_group_id = None  # For now
        self.geographical_group_type = None  # For now
        self.measurement_position = None  # For now
        self.result_quality = ResultQuality()

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['geographical_group_id'], **kwargs)

    def __eq__(self, other):
        return self.id == other.id


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
        - *result_quality:*, string,
        - *geographical_group_id:* string, River system ID (Region ID)
        - *geographical_group_type:* enum (sampling_feature, site, plot, region, point_location, measurement position)
        - *measurement_position:* float, height or depth of observation

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


class DataPointGroup(Base):
    """
    Series of data points grouped by time, space, model, sample  etc. Anything specified at the
    group  level automatically applies to the individual data point.

    Attributes:
        - *id:* string,
        - *units:* Unit
        - *timestamp_utc_offset:* float (offset in hours), +9
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* enum (sampling_feature, site, plot, region, point_location, measurement position)
        - *measurement:* string, (optional)
        - *measurement_position:* The position at which the measurement was taken
        - *data_points:* Array of Time Value pairs

    """
    def __init__(self, datasource, **kwargs):
        self.id = None
        self.units = None
        self.measurement_id = None
        self.utc_offset = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.measurement_position = None  # For now,
        self.data_points = None

        if "measure_variable" in kwargs:

            synth_param = get_datasource_variable(datasource, kwargs["measure_variable"])
            measurement = get_datasource_measurement(datasource,synth_param.measure_variable_id)
            kwargs['measurement_id']=measurement.id
            kwargs.pop("measure_variable")

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['geographical_group_id'], **kwargs)

    def __eq__(self, other):
        return self.id == other.id


class DataPoint(Base):
    """
    Generic Data Point (what, where, when??)

    Attributes:
        - *id:* string (optional),
        - *measurement:* string,
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* en um (sampling_feature, site, plot, region)
        - *units:* Unit
        - *measurement_position:* The position at which the measurement was taken
        - *qaqc:* Has this data been quality checked?
    """
    def __init__(self, datasource, **kwargs):
        self.id = None
        self.measurement_id = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.units = None
        self.measurement_position = None  # For now,
        self.measurement = None
        self.quality_checked = None

        if "measure_variable" in kwargs:

            synth_param = get_datasource_variable(datasource, kwargs["measure_variable"])
            self.measurement = get_datasource_measurement(datasource, synth_param.measure_variable_id)
            kwargs.pop("measure_variable")

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['geographical_group_id'], **kwargs)


class ImageDataPoint(DataPoint):
    """
    Representing any imaging result

    Inherited attributes (:class:`DataPoint`):
        - *id:* string
        - *measurement_id:* string
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* enum (sampling_feature, site, plot, region)
        - *units:* Unit

    Attributes:
        - *size:* float,
        - *resolution:* float,
        - *image:* an URL (for now)

    """
    def __init__(self, datasource, **kwargs):
        self.size = None
        self.resolution = None
        self.image = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)


class TimeSeriesDataPoint(DataPoint):
    """
    Time series data point

    Inherited attributes (:class:`DataPoint`):
        - *id:* string
        - *measurement_id:* string
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* enum (sampling_feature, site, plot, region)

    Attributes:
        - *timestamp:* datetime
        - *value:* float
        - *temporal_resolution:* enum(year, month, day, hour, minute, second, millisecond)
        - *reference:* string (start, middle, end)
        - *utc_offset:* float (offset in hours) - optional
    """

    REFERENCE_START = "start"
    REFERENCE_MIDDLE = "middle"
    REFERENCE_END = "end"

    TEMPORAL_RESOLUTION_YEAR = "year"
    TEMPORAL_RESOLUTION_MONTH = "month"
    TEMPORAL_RESOLUTION_DAY = "day"
    TEMPORAL_RESOLUTION_HOUR = "hour"
    TEMPORAL_RESOLUTION_MINUTE = "minute"
    TEMPORAL_RESOLUTION_SECOND = "second"

    def __init__(self, datasource, **kwargs):
        self.timestamp = None
        self.value = None
        self.temporal_resolution = None
        self.reference = None
        self.utc_offset = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
