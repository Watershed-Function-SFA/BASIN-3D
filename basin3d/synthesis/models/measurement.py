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
from basin3d.synthesis.models import Base


class DataPointGroup(Base):
    """
    Series of data points grouped by time, space, model, sample  etc. Anything specified at the
    group  level automatically applies to the individual data point.

    Attributes:
        - *id:* string,
        - *measurement:* string, (optional)
        - *start_time:* datetime,  survey start time (month/year)
        - *end_time:* datetime, units: survey end time (month/year)
        - *timestamp_utc_offset:* float (offset in hours), +9
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* enum (sampling_feature, site, plot, region, point_location, measurement position)
        - *results:* Array of DataPoint objects

    """
    def __init__(self, datasource, **kwargs):
        self.id = None
        self.measurement_id = None
        self.start_time = None
        self.end_time = None
        self.utc_offset = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.results = []

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
        - *geographical_group_type* enum (sampling_feature, site, plot, region)
        - *units:* Unit
        - *measurement_position:* The position at which the measurement was taken
    """
    def __init__(self, datasource, **kwargs):
        self.id = None
        self.measurement_id = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.units = None
        self.measurement_position = None  # For now,
        self.measurement = None

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
