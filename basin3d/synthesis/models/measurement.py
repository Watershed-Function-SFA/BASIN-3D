"""


`basin3d.synthesis.models.measurement`
**************************************

.. currentmodule:: basin3d.synthesis.models.simulations

:synopsis: Classes to represent Simulation/Modeling Concepts


---------------------
"""
from basin3d.synthesis.models import Base


class DataPointGroup(Base):
    """
    Series of data points grouped by time, space, model, sample  etc. Anything specified at the
    group  level automatically applies to the individual data point.

    Attributes:
        - *id:* string, Cs137 MR survey ID
        - *measurement_id:* string, Cs137MID
        - *start_time:* datetime,  survey start time (month/year)
        - *end_time:* datetime, units: survey end time (month/year)
        - *timestamp_utc_offset:* float (offset in hours), +9
        - *geographical_group_id:* string, River system ID (Region ID).
        - *geographical_group_type* enum (sampling_feature, site, plot, model_domain, region): Model_domain (or optionally region)
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
        - *id:* string,
        - *measurement_id:* string,
        - *sampling_feature_id:* string (sampling feature can be site/plot/measurement location),
        - *unit:* Unit
    """
    def __init__(self, datasource, **kwargs):
        self.id = None
        self.measurement_id = None
        self.sampling_feature_id = None
        self.units = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    def __eq__(self, other):
        return self.id == other.id


class MeasurementTimeSeriesDataPoint(DataPoint):
    """
    Time_series data point

    Attributes:
        - *id:* string,
        - *measurement_id:* string,
        - *sampling_feature_id:* string (sampling feature can be site/plot/measurement location),
        - *unit:* Unit
        - *timestamp: datetime,
        - *value: float,
        - *units: Unit  Cs137UID
        - *temporal_resolution: enum(year, month, day, hour, minute, second, millisecond),
        - *reference: string (start, middle, end),
        - *utc_offset: float (offset in hours) - optional
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
        super().__init__(datasource,  datasource_ids=['geographical_group_id'], **kwargs)

    def __eq__(self, other):
        return self.id == other.id