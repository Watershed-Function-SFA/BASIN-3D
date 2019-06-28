"""
`basin3d.synthesis.models.measurement`
**************************************

.. currentmodule:: basin3d.synthesis.models.measurement

:synopsis: Classes to represent Observations

.. inheritance-diagram:: basin3d.synthesis.models basin3d.synthesis.models.measurement
    :parts: 2

---------------------
"""
from collections import namedtuple
from numbers import Number
from typing import List

from basin3d.models import FeatureTypes, ObservedPropertyVariable
from basin3d.synthesis.models.field import MonitoringFeature
from basin3d.plugins import get_datasource_observed_property, \
    get_datasource_observed_property_variable
from basin3d.synthesis.models import Base
from django.utils.datetime_safe import datetime


class TimeValuePair(namedtuple('TimeValuePair', ['timestamp', 'value'])):
    """
    Tuple that represents a time value pair.  This will handle timestamp conversion

    `(timestamp, value)`
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
    Controlled Vocabulary for result quality assessment
    """

    #: The result has been checked for quality
    RESULT_QUALITY_CHECKED = "CHECKED"

    #: The result is raw or unchecked for quality
    RESULT_QUALITY_UNCHECKED = "UNCHECKED"


class Observation(Base):
    """

    OGC OM_Observation feature type. This is a parent class to which Mixins
        should be added to create observation types with metadata and result.
    """

    #: Measurement Time Value Pair Timeseries
    TYPE_MEASUREMENT_TVP_TIMESERIES = "MEASUREMENT_TVP_TIMESERIES"

    #: A measurement
    TYPE_MEASUREMENT = "MEASUREMENT"

    def __init__(self, datasource, **kwargs):
        self._id = None
        self._type = None
        self._utc_offset = None
        self._phenomenon_time = None
        self._observed_property = None
        self._feature_of_interest = None
        self._feature_of_interest_type = None
        self._result_quality = ResultQuality()

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
        self.__validate__()

    def __eq__(self, other):
        return self.id == other.id

    def __validate__(self):
        """
        Validate attributes
        """

        # Validate feature of interest type if present is class FeatureTypes
        if self.feature_of_interest_type and self.feature_of_interest_type not in FeatureTypes.TYPES.keys():
            raise AttributeError("feature_of_interest_type must be FeatureType")

    @property
    def id(self) -> str:
        """Unique observation identifier"""
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def type(self) -> str:
        """Type of observation. Use constants prefixed with `TYPE_`"""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def utc_offset(self) -> int:
        """Coordinated Universal Time (UTC) offset in hours (e.g. +/-9)"""
        return self._utc_offset

    @utc_offset.setter
    def utc_offset(self, value: int):
        self._utc_offset = value

    @property
    def phenomenon_time(self) -> str:
        """datetime of the observation (required OGC attribute timePhenomenon).
           For timeseries, start and end datetimes can be provided."""
        return self._phenomenon_time

    @phenomenon_time.setter
    def phenomenon_time(self, value: str):
        self._phenomenon_time = value

    @property
    def observed_property(self) -> str:
        """The property that was observed"""
        return self._observed_property

    @observed_property.setter
    def observed_property(self, value: str):
        self._observed_property = value

    @property
    def feature_of_interest(self) -> 'MonitoringFeature':
        """The feature on which the observed property was observed"""
        return self._feature_of_interest

    @feature_of_interest.setter
    def feature_of_interest(self, value: 'MonitoringFeature'):
        self._feature_of_interest = value

    @property
    def feature_of_interest_type(self) -> 'FeatureTypes':
        """The type of feature that was observed. See :class:`basin3d.models.FeatureTypes`"""
        return self._feature_of_interest_type

    @feature_of_interest_type.setter
    def feature_of_interest_type(self, value: 'FeatureTypes'):
        self._feature_of_interest_type = value

    @property
    def result_quality(self) -> 'ResultQuality':
        """The result quality assessment. See :class:`ResultQuality`"""
        return self._result_quality

    @result_quality.setter
    def result_quality(self, value: 'ResultQuality'):
        self._result_quality = value


class TimeMetadataMixin(object):
    """
    Metadata attributes for Observations with a time
    """

    #: Observations aggregated by year
    AGGREGATION_DURATION_YEAR = "YEAR"

    #: Observations aggregated by month
    AGGREGATION_DURATION_MONTH = "MONTH"

    #: Observations aggregated by day
    AGGREGATION_DURATION_DAY = "DAY"

    #: Observations aggregated by hour
    AGGREGATION_DURATION_HOUR = "HOUR"

    #: Observations aggregated by minute
    AGGREGATION_DURATION_MINUTE = "MINUTE"

    #: Observations aggregated by second
    AGGREGATION_DURATION_SECOND = "SECOND"

    #: Observation taken at the start
    TIME_REFERENCE_START = "START"

    #: Observation taken in the middle
    TIME_REFERENCE_MIDDLE = "MIDDLE"

    #: Observation taken at the end
    TIME_REFERENCE_END = "END"

    def __init__(self, *args, **kwargs):
        self._aggregation_duration = None
        self._time_reference_position = None

        # Instantiate the serializer superclass
        super(TimeMetadataMixin, self).__init__(*args, **kwargs)

    @property
    def aggregation_duration(self) -> str:
        """Time period represented by the observation. Follows OGC TM_PeriodDuration.
           Use constants prefixed with `AGGREGATION_DURATION`"""
        return self._aggregation_duration

    @aggregation_duration.setter
    def aggregation_duration(self, value: str):
        self._aggregation_duration = value

    @property
    def time_reference_position(self) -> str:
        """Position of timestamp in aggregated_duration. Encompassed as part of OGC interpolationType.
           Use constants prefixed with `TIME_REFERENCE`"""
        return self._time_reference_position

    @time_reference_position.setter
    def time_reference_position(self, value: str):
        self._time_reference_position = value


class MeasurementMetadataMixin(object):
    """
    Metadata attributes for Observations type Measurement
    """

    #: Statistical Mean
    STATISTIC_MEAN = "MEAN"

    #: Statistical Minimum
    STATISTIC_MIN = "MIN"

    #: Statistical Maximum
    STATISTIC_MAX = "MAX"

    #: Statistical Sum
    STATISTIC_TOTAL = "TOTAL"

    def __init__(self, *args, **kwargs):
        self._observed_property_variable = None
        self._statistic = None

        # Instantiate the serializer superclass
        super(MeasurementMetadataMixin, self).__init__(*args, **kwargs)

    @property
    def observed_property_variable(self) -> 'ObservedPropertyVariable':
        """The observed property that was measured"""
        return self._observed_property_variable

    @observed_property_variable.setter
    def observed_property_variable(self, value: 'ObservedPropertyVariable'):
        self._observed_property_variable = value

    @property
    def statistic(self) -> str:
        """The statistical property of the observation result. Use constants prefixed with `STATISTIC_`"""
        return self._statistic

    @statistic.setter
    def statistic(self, value: str):
        self._statistic = value


class MeasurementTimeseriesTVPResultMixin(object):
    """
    Result Mixin: Measurement Timeseries TimeValuePair
    """
    def __init__(self, *args, **kwargs):
        self._result_points = []
        self._unit_of_measurement = None

        # Instantiate the serializer superclass
        super(MeasurementTimeseriesTVPResultMixin, self).__init__(*args, **kwargs)

    @property
    def result_points(self) -> List['TimeValuePair']:
        """A list of results """
        return self._result_points

    @result_points.setter
    def result_points(self, value: List['TimeValuePair']):
        self._result_points = value

    @property
    def unit_of_measurement(self) -> str:
        """Unit of measurement"""
        return self._unit_of_measurement

    @unit_of_measurement.setter
    def unit_of_measurement(self, value: str):
        self._unit_of_measurement = value


class MeasurementResultMixin(object):
    """
    Result Mixin: Measurement
    """
    def __init__(self, *args, **kwargs):
        self._result_value = None
        self._unit_of_measurement = None

        # Instantiate the serializer superclass
        super(MeasurementResultMixin, self).__init__(*args, **kwargs)

    @property
    def result_value(self):
        """Numeric value that was measured"""
        return self._result_value

    @result_value.setter
    def result_value(self, value):
        self._result_value = value

    @property
    def unit_of_measurement(self):
        """Unit of measurement"""
        return self._unit_of_measurement

    @unit_of_measurement.setter
    def unit_of_measurement(self, value):
        self._unit_of_measurement = value


class MeasurementTimeseriesTVPObservation(TimeMetadataMixin, MeasurementMetadataMixin,
                                          MeasurementTimeseriesTVPResultMixin, Observation):
    """
    Series of measurement (numerical) observations in TVP format grouped by time (i.e., a timeseries).
    Anything specified at the group level automatically applies to the individual observation.
    """
    # NOTE: Position Observation (the one inheriting from Base) last in the inheritance list.
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
