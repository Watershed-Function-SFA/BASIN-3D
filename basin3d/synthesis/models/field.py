"""
`basin3d.synthesis.models.field`
********************************

.. currentmodule:: basin3d.synthesis.models.field

:synopsis: Classes to represent Multi-scale Spatial Hierarchy for Field Observations

* :class:`AltitudeCoordinate` - The reference frame or system from which altitudes (elevations) are measured.
* :class:`DepthCoordinate` -  The reference frame or system from which depths are measured.
* :class:`GeographicCoordinate` - The quantities of latitude and longitude which define the position of a point on
    the Earth's surface with respect to a reference spheroid.
* :class:`HorizontalCoordinate` - Generic XY coordinates for a point on earth
* :class:`MeasurementPosition` - Sublocation within a point location
* :class:`Plot` -  A group of related point measurements
* :class:`PointLocation` - A point on the earth where something is being measured
* :class:`Region` - An arbitrary area
* :class:`SamplingFeature` - Base class.  A feature where sampling is conducted.
* :class:`Site` - A demarcated, geographic area where measurements are being conducted.
* :class:`VerticalCoordinate` - The reference frame or system from which vertical distances (altitudes or depths) are measured.

"""

from basin3d.synthesis.models import Base


class VerticalCoordinate(Base):
    """
    The reference frame or system from which vertical distances (altitudes or depths) are measured.

    Attributes:
        *type:* enum ("altitude”, "depth),
        *value:* float, datum_name: string,
        *vertical_resolution:* float,
        *vertical_distance_units:* enum  ("meters", "feet"),
        *encoding_method:* "Explicit coordinate included with horizontal coordinates", "Implicit coordinate", "Attribute values")
    """
    TYPE_ALTITUDE = "altitude"
    TYPE_DEPTH = "depth"

    DISTANCE_UNITS_METERS = "meters"
    DISTANCE_UNITS_FEET = "feet"

    ENCODING_EXPLICIT = "explicit"
    ENCODING_IMPLICIT = "implicit"
    ENCODING_ATTRIBUTE = "attribute"

    def __init__(self, **kwargs):
        self.value = None
        self.vertical_resolution = None
        self.vertical_distance_units = None
        self.encoding_method = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)


class AltitudeCoordinate(VerticalCoordinate):
    """
    The reference frame or system from which altitudes (elevations) are measured. The term
    "altitude" is used instead of the common term "elevation" to conform to the terminology
    in Federal Information Processing Standards 70-1 and 173.

    Attributes:
        *datum_name:*
            + **NGVD29** "National Geodetic Vertical Datum of 1929"
            + **NAVD88** "North American Vertical Datum of 1988"
    """
    DATUM_NGVD29 = "NGVD29"
    DATUM_NAVD88 = "NAVD88"

    def __init__(self, **kwargs):
        self.datum = None

        # Initialize after the attributes have been set
        super().__init__(type=self.TYPE_ALTITUDE, **kwargs)


class DepthCoordinate(VerticalCoordinate):
    """
    The reference frame or system from which depths are measured.

    Attributes:
        + datum_name:
            + **LS** "Local surface"
            + **MSL** "Mean sea level"
    """
    DATUM_LOCAL_SURFACE = "LS"
    DATUM_MEAN_SEA_LEVEL = "MSL"

    def __init__(self, **kwargs):
        self.datum = None

        # Initialize after the attributes have been set
        super().__init__(type=self.TYPE_DEPTH, **kwargs)


class HorizontalCoordinate(Base):
    """Generic XY coordinates for a point on earth (https://www.fgdc.gov/csdgmgraphical/spref.htm)
    
    Attributes: 
        + *x:* float
        + *y:* float
        + *datum:* enum ("WGS84”, "NAD27”, "NAD83”), 
        + *type:* enum ("geographic”,”planar_grid”,”planar_local”, "planar_map_projection”, "local”)
    """

    DATUM_WGS84 = "WGS84"
    DATUM_NAD83 = "NAD83"
    DATUM_NAD27 = "NAD27"

    TYPE_GEOGRAPHIC = "geographic"
    TYPE_PLANAR_GRID = "planar_grid"
    TYPE_PLANAR_LOCAL = "planar_local"
    TYPE_PLANAR_MAP_PROJECTION = "planar_map_projection"
    TYPE_LOCAL = "local"

    def __init__(self, **kwargs):
        self.x = None
        self.y = None
        self.datum = None
        self.type = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)


class GeographicCoordinate(HorizontalCoordinate):
    """
    The quantities of latitude and longitude which define the position of a point on 
    the Earth's surface with respect to a reference spheroid. (https://www.fgdc.gov/csdgmgraphical/spref.htm)
    
    Attributes: 
        + *latitude:*
        + *longitude:*
        + *units:* units determine the datatypes of latitude and longitude
            + **DD** "Decimal degrees"
            + **DM** "Decimal minutes"
            + **DS** "Decimal seconds"
            + **DDM** "Degrees and decimal minutes"
            + **DMDS** "Degrees, minutes, and decimal seconds"
            + **Radians** "Radians"
            + **Grads** "Grads")

    """

    UNITS_DEC_DEGREES = "DD"
    UNITS_DEC_MINUTES = "DM"
    UNITS_DEC_SECONDS = "DS"
    UNITS_DEGREES_DEC_MINUTES = "DDM"
    UNITS_DEGREES_MIN_DEC_SECS = "DMDS"
    UNITS_RADIANS = "Radians"
    UNITS_GRADS = "Grads"

    UNITS = {UNITS_DEC_DEGREES: "Decimal degrees",
             UNITS_DEC_MINUTES: "Decimal minutes",
             UNITS_DEC_SECONDS: "Decimal seconds",
             UNITS_DEGREES_DEC_MINUTES: "Degrees and decimal minutes",
             UNITS_DEGREES_MIN_DEC_SECS: "Degrees, minutes, and decimal seconds",
             UNITS_RADIANS: UNITS_RADIANS,
             UNITS_GRADS: UNITS_GRADS
             }

    UNITS_DATA_TYPES = {UNITS_DEC_DEGREES: float,
                        UNITS_DEC_MINUTES: float,
                        UNITS_DEC_SECONDS: float,
                        UNITS_DEGREES_DEC_MINUTES: (int, float),
                        UNITS_DEGREES_MIN_DEC_SECS: (int, int, int),
                        UNITS_RADIANS: float,
                        UNITS_GRADS: float
                        }

    def __init__(self, **kwargs):
        self.units = None

        if "longitude" in kwargs:
            kwargs["x"] = kwargs["longitude"]
            kwargs.pop("longitude")
        if "latitude" in kwargs:
            kwargs["y"] = kwargs["latitude"]
            kwargs.pop("latitude")

        # Initialize after the attributes have been set
        super().__init__(type=self.TYPE_GEOGRAPHIC, **kwargs)
        self.__validate__()

    def __validate__(self):
        """
        Validate the attributes
        """

        # Validate that the units are valid
        if self.units not in self.UNITS.keys():
            raise AttributeError("{} is not a valid unit. Must be in {}".format(self.units,
                                                                                ",".join(
                                                                                    self.UNITS.keys())))

        # Validate that the unit values for x and y are the correct type
        units_data_type = self.UNITS_DATA_TYPES[self.units]
        for attribute in {'x', 'y'}:
            value = getattr(self, attribute)
            if self.units and value:
                if isinstance(units_data_type, tuple):

                    if not isinstance(value, tuple) or len(units_data_type) != len(value):
                        raise TypeError("Value {} for {}.{}  must be type {}({})".format(value,
                                                                                         self.__class__.__name__,
                                                                                         attribute,
                                                                                         type(
                                                                                             units_data_type).__name__,
                                                                                         ",".join([
                                                                                                      x.__name__
                                                                                                      for
                                                                                                      x
                                                                                                      in
                                                                                                      units_data_type])))
                    else:
                        for idx, v in enumerate(value):
                            if not isinstance(v, units_data_type[idx]):
                                raise TypeError("Value {} for {}.{}  must be type {}({})".format(
                                    value,
                                    self.__class__.__name__,
                                    attribute,
                                    type(units_data_type).__name__,
                                    ",".join([x.__name__ for x in units_data_type])))

                elif not isinstance(value, units_data_type):
                    raise TypeError("Value {} for {}.{} must be type '{}' not '{}'".format(value,
                                                                                           self.__class__.__name__,
                                                                                           attribute,
                                                                                           units_data_type.__name__,
                                                                                           type(
                                                                                               value).__name__))

    @property
    def latitude(self):
        return self.x

    @property
    def longitude(self):
        return self.y


class Region(Base):
    """
    A Region is any arbitrary area - not necessarily associated with any
    observations - e.g. a watershed, a city

    Attributes:
        - *id:* string
        - *name:* string
        - *description:* string
        - *geom:* polygon
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.description = None
        self.geom = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)


class SamplingFeature(Base):
    """
    A feature where sampling is conducted. These can be of many types- a Site, a plot, a transect,
    a point location etc.). Can be nested infinitely? Concept from ODM2/OGC
    (types: http://vocabulary.odm2.org/samplingfeaturetype/ ).

    Attributes:
        *id:* string
        *name:* string
        *description:* string
        *type:* string
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.description = None
        self.type = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)


class Site(SamplingFeature):
    """
    A demarcated, geographic area where measurements are being conducted. E.g. East River Site,
    K34-Manaus. Note: (Site differs from ODM 2 definition of a site, which is a point location.
    It would be very confusing for us to adopt that terminology since that is not how a majority
    of our users think about sites - this has been proven in at least 2 of our projects).

    Attributes (including those inherited):
        *id:* string
        *name:* string
        *description:* string
        *type:* string ("site")
        *country:* string
        *state_province:* string
        *utc_offset:* integer
        *center_coordinates:* Coordinates
        *geom:* polygon,
        *contacts:* Array of Person objects,
        *PI:* Person,
        *urls:* Array of strings.

        If needed we could add bounding box UL and LR coordinates later.
    """

    def __init__(self, datasource, **kwargs):
        self.country = None
        self.state_province = None
        self.utc_offset = 0
        self.center_coordinates = None
        self.geom = None
        self.contacts = []
        self.pi = None
        self.urls = []

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
        self.type = str(self.__class__.__name__).lower()


class Plot(SamplingFeature):
    """
    A group of related point measurements - such as in a plot or a set of wells

    Attributes (including those inherited):
        *id:* string
        *name:* string
        *description:* string
        *type:* string ("plot")
        *site_id:* string,
        *geom:* polygon,
        *pi:* Person
    """

    def __init__(self, datasource, **kwargs):
        self.site_id = None
        self.geom = None
        self.pi = None

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['site_id'], **kwargs)

        self.type = str(self.__class__.__name__).lower()


class PointLocation(SamplingFeature):
    """
    This is a point on the earth where something is being measured - e.g. a well,
    a stream gage, a tree, a tower. New Broker terminology..

    See http://maps.waterdata.usgs.gov/mapper/help/sitetype.html &
    http://vocabulary.odm2.org/samplingfeaturetype/

    Attributes:
        *id:* string
        *name:* string
        *description:* string
        *type:* enum (well, gage etc.)
        *site_id:* string (establishes parent-child relationship),
        *geographical_group:* string (plot_id or site_id),
        *horizontal_coordinate:* HorizontalCoordinate,
        *vertical_extent:* VerticalCoordinate (this is optional).
        *position:* :class:`MeasurementPosition`
    """

    def __init__(self, datasource, **kwargs):
        self.site_id = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.horizontal_coordinate = None
        self.vertical_extent = None
        self.position = None

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['site_id', 'geographical_group_id'], **kwargs)


class MeasurementPosition(Base):
    """(MAYBE THIS SHOULD BE SPECIFIC TYPES OF MEASUREMENT POSITIONS.. WELL MEASUREMENT,
    TOWER SENSORS, TREE PROBES - NEED DIFFERENT INFO)

    Sublocation within a point location - depth, sensors around a tree.
    Adopted from Danielle’s metadata framework.

    Attributes:
        *type:* enum ("Point3D?”)
        *depth_height:* float (+ve for height, -ve for depth)
        *depth_height_units:* string
    """

    def __init__(self, **kwargs):
        self.depth_height = None
        self.depth_height_units = None
        self.type = "point-3d"

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
