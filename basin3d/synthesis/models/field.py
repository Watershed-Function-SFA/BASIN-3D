"""
`basin3d.synthesis.models.field`
********************************

.. currentmodule:: basin3d.synthesis.models.field

:synopsis: Classes to represent multi-scale feature hierarchy on which Observations are made

---------------------
"""
from typing import List

from basin3d.models import FeatureTypes, SpatialSamplingShapes
from basin3d.plugins import get_datasource_observed_property_variables
from basin3d.synthesis.models import Base, Person  # pass Person for plugins


class RelatedSamplingFeature(Base):
    """
    Class that represents a related sampling feature and its role relative to
    the sampling feature to which it is related. Spatial hierarchies of features
    are built by specifying related sampling features.

    Data model from OGC Observations and Measurements.
    """

    #: Sampling Feature is a parent
    ROLE_PARENT = "PARENT"

    ROLE_TYPES = [ROLE_PARENT]

    def __init__(self, datasource, **kwargs):
        self._related_sampling_feature: 'SamplingFeature' = None
        self._related_sampling_feature_type: str = None
        self._role: str = None

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['related_sampling_feature'], **kwargs)
        self.__validate__()

    def __validate__(self):
        """
        Validate attributes
        :return:
        """
        # ToDo: refactor this to not require type
        if self.related_sampling_feature_type is not None and \
                self.related_sampling_feature_type not in FeatureTypes.TYPES.keys():
            raise AttributeError("RelatedSamplingFeature related_sampling_feature_type must be FeatureTypes")

        if self.role is None:
            raise AttributeError("RelatedSamplingFeature role is required.")
        elif self.role not in RelatedSamplingFeature.ROLE_TYPES:
            raise AttributeError("RelatedSamplingFeature role must be one of predefined roles.")

    @property
    def related_sampling_feature(self) -> 'SamplingFeature':
        """A sampling feature relation"""
        return self._related_sampling_feature

    @related_sampling_feature.setter
    def related_sampling_feature(self, value: 'SamplingFeature'):
        self._related_sampling_feature = value

    @property
    def related_sampling_feature_type(self) -> str:
        """Feature type of the related sampling feature. See :class:`FeatureTypes` for a list of types"""
        return self._related_sampling_feature_type

    @related_sampling_feature_type.setter
    def related_sampling_feature_type(self, value: str):
        self._related_sampling_feature_type = value

    @property
    def role(self) -> str:
        """Currently the only Related Sampling Feature role is a :class:`RelatedSamplingFeature.PARENT`"""
        return self._role

    @role.setter
    def role(self, value: str):
        self._role = value


class Coordinate(Base):
    """
    Top level coordinate class that holds :class:`AbsoluteCoordinate` or :class:`RepresentativeCoordinate`
    """

    def __init__(self, **kwargs):
        self._absolute: AbsoluteCoordinate = None
        self._representative: RepresentativeCoordinate = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
        self.__validate__()

    def __validate__(self):
        """
        Validate the attributes
        """

        # enforce absolute is class AbsoluteCoordinate
        if self.absolute and not isinstance(self.absolute, AbsoluteCoordinate):
            raise TypeError("Coordinate.absolute attribute must be AbsoluteCoordinate object")

        # enforce representative class is RepresentativeCoordinate
        if self.representative and not isinstance(self.representative, RepresentativeCoordinate):
            raise TypeError("Coordinate.representative attribute must be RepresentativeCoordinate object")

        # enforce required coordinates: if only representative, then representative.representative_point is required
        # if self.absolute is None:
        #     if self.representative.representative_point is None:
        #         raise AttributeError("Representative_point is required if only representative coordinates are provided.")

    @property
    def absolute(self) -> 'AbsoluteCoordinate':
        """Absolute coordinate"""
        return self._absolute

    @absolute.setter
    def absolute(self, value: 'AbsoluteCoordinate'):
        self._absolute = value

    @property
    def representative(self) -> 'RepresentativeCoordinate':
        """Representative coordinate"""
        return self._representative

    @representative.setter
    def representative(self, value: 'RepresentativeCoordinate'):
        self._representative = value


class AbsoluteCoordinate(Base):
    """
    Absolute coordinate describes the geo-referenced location of a feature.
    Coordinates match the feature's shape. For example, a curve is a list of points.
    Currently collections of discrete points describing a feature are supported.

    """
    # Planned extension to better check point, curve, surface, solid shape-specific coordinates.
    # May want to include a type attribute akin to GeoJSON type
    # In future, reconsider the format of attributes to allow for more types of description (meshes, solids, etc)

    def __init__(self, **kwargs):
        self._horizontal_position: List[GeographicCoordinate] = []
        self._vertical_extent: List[AltitudeCoordinate] = []

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
        self.__validate__()

    def __validate__(self):
        # require horizontal position and vertical extent to be lists
        if not isinstance(self.horizontal_position, (list, tuple, set)):  # check for better not iterable
            self.horizontal_position = [self.horizontal_position]

        if not isinstance(self.vertical_extent, (list, tuple, set)):
            self.vertical_extent = [self.vertical_extent]

        # ToDo: validate obj types
        for obj in self.horizontal_position:
            if not isinstance(obj, GeographicCoordinate):
                raise TypeError("Horizontal position must be instance of GeographicCoordinate")

        if len(self.vertical_extent) > 0:
            for obj in self.vertical_extent:
                if not isinstance(obj, AltitudeCoordinate):
                    raise TypeError("Vertical extent must be instance of AltitudeCoordinate")

            if len(self.horizontal_position) != len(self.vertical_extent):
                raise AttributeError("Lengths of horizontal positions and vertical extent must be equal.")

        # ToDo: add validation for shape coordinates.

    @property
    def horizontal_position(self) -> List['GeographicCoordinate']:
        """list of obj :class:`GeographicCoordinate`"""
        return self._horizontal_position

    @horizontal_position.setter
    def horizontal_position(self, value: List['GeographicCoordinate']):
        self._horizontal_position = value

    @property
    def vertical_extent(self) -> List['AltitudeCoordinate']:
        """list of obj :class:`AltitudeCoordinate`"""
        return self._vertical_extent

    @vertical_extent.setter
    def vertical_extent(self, value: List['AltitudeCoordinate']):
        self._vertical_extent = value


class RepresentativeCoordinate(Base):
    """
    Representative coordinates describe the location of a feature by a representative shape / location.
    For example, a study area may be represented by the center point.
    The veritical position from a reference position (e.g., height, depth) is also described in this class.
    Currently representative points are supported. The class is extendable to other forms of representing
    (e.g., diameter, area, side_length)
    Representative point types are also expandable as use cases require.
    """

    #: Placement of the representative point is the center of a local surface
    REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE = "CENTER LOCAL SURFACE"

    #: Placement of the representative point is the upper left corner (northwest)
    REPRESENTATIVE_POINT_TYPE_UPPER_LEFT_CORNER = "UPPER LEFT CORNER"

    #: Placement of the representative point is the upper right corner (northeast)
    REPRESENTATIVE_POINT_TYPE_UPPER_RIGHT_CORNER = "UPPER RIGHT CORNER"

    #: Placement of the representative point is the lower left corner (southhwest)
    REPRESENTATIVE_POINT_TYPE_LOWER_LEFT_CORNER = "LOWER LEFT CORNER"

    #: Placement of the representative point is the lower right corner (northeast)
    REPRESENTATIVE_POINT_TYPE_LOWER_RIGHT_CORNER = "LOWER RIGHT CORNER"

    def __init__(self, **kwargs):
        self._representative_point: AbsoluteCoordinate = None
        self._representative_point_type: str = None
        self._vertical_position: DepthCoordinate = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
        self.__validate__()

    def __validate__(self):
        """
        Validate attributes
        """

        # if representative point, require representative point type
        # if self.representative_point is not None:
        #     if self.representative_point_type is None:
        #         raise AttributeError("representative_point_type is required if representative_point provided.")

    @property
    def representative_point(self) -> AbsoluteCoordinate:
        """A point representation of the feature.
           obj :class:`AbsoluteCoordinate` for POINT"""
        return self._representative_point

    @representative_point.setter
    def representative_point(self, value: AbsoluteCoordinate):
        self._representative_point = value

    @property
    def representative_point_type(self) -> str:
        """The type of representative point relative to the feature's geometry
           Currently the point is assumed to be located at the local surface (CV).
           Use constants prefixed with `REPRESENTATIVE_POINT_TYPE_` """
        return self._representative_point_type

    @representative_point_type.setter
    def representative_point_type(self, value: str):
        self._representative_point_type = value

    @property
    def vertical_position(self) -> 'DepthCoordinate':
        """The vertical position of the feature from a reference position (e.g., height or depth).
           obj :class:`DepthCoordinate`"""
        return self._vertical_position

    @vertical_position.setter
    def vertical_position(self, value: 'DepthCoordinate'):
        self._vertical_position = value


class VerticalCoordinate(Base):
    """
    The vertical position of the feature (altitudes or depths).
    The reference frame or system is specified.

    """
    #: The distance above or below sea level (elevation)
    TYPE_ALTITUDE = "ALTITUDE"

    #: The distance above (height) or below (depth) of the local surface
    TYPE_DEPTH = "DEPTH"

    #: Distance in meters
    DISTANCE_UNITS_METERS = "meters"

    #: Distance in feet
    DISTANCE_UNITS_FEET = "feet"

    #: Explicit coordinate included with horizontal coordinates
    ENCODING_EXPLICIT = "EXPLICIT"

    #: Implicit coordinate
    ENCODING_IMPLICIT = "IMPLICIT"

    #: Attribute values
    ENCODING_ATTRIBUTE = "ATTRIBUTE"

    def __init__(self, **kwargs):
        self._value: float = None
        self._resolution: float = None
        self._distance_units: str = None
        self._encoding_method: str = None
        self._datum: str = None
        self._type: str = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)

    @property
    def type(self) -> str:
        """The type of veritical position :class:`VerticalCoordinate.TYPE_ALTITUDE` or
           :class:`VerticalCoordinate.TYPE_DEPTH`"""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def datum(self) -> str:
        """
        The reference coordinate system. Use constants prefixed with `DATUM_`
        """
        return self._datum

    @datum.setter
    def datum(self, value: str):
        self._datum = value

    @property
    def encoding_method(self) -> str:
        """The method for encoding the units of distance. Use constants prefixed with `ENCODING_` """
        return self._distance_units

    @encoding_method.setter
    def encoding_method(self, value: str):
        self._encoding_method = value

    @property
    def distance_units(self) -> str:
        """The unit of distance. It uses constants prefixed with `DISTANCE_UNITS_`"""
        return self._distance_units

    @distance_units.setter
    def distance_units(self, value: str):
        self._distance_units = value

    @property
    def resolution(self) -> float:
        """The minimum distance possible between two adjacent
           depth values, expressed in Distance Units used for Depth"""
        return self._resolution

    @resolution.setter
    def resolution(self, value: float):
        self._resolution = value

    @property
    def value(self) -> float:
        """The vertical position value"""
        return self._value

    @value.setter
    def value(self, value: float):
        self._value = value


class AltitudeCoordinate(VerticalCoordinate):
    """
    An altitudinal vertical position (i.e., distance from sea level).
    The reference frame or system is specified. The term
    "altitude" is used instead of the common term "elevation" to conform to the terminology
    in Federal Information Processing Standards 70-1 and 173.
    """

    #: National Geodetic Vertical Datum of 1929
    DATUM_NGVD29 = "NGVD29"

    #: North American Vertical Datum of 1988
    DATUM_NAVD88 = "NAVD88"

    def __init__(self, **kwargs):
        self._datum: str = None

        # Initialize after the attributes have been set
        super().__init__(type=self.TYPE_ALTITUDE, **kwargs)

    @property
    def datum(self) -> str:
        """The reference coordinate system. Use constants prefixed with `DATUM_`"""
        return self._datum

    @datum.setter
    def datum(self, value: str):
        self._datum = value


class DepthCoordinate(VerticalCoordinate):
    """
    A depth vertical position (i.e., the height or depth from the specified reference position)
    The reference frame or system is specified.
    """

    #: Local surface
    DATUM_LOCAL_SURFACE = "LS"

    #: Mean sea level
    DATUM_MEAN_SEA_LEVEL = "MSL"

    def __init__(self, **kwargs):
        self._datum = None

        # Initialize after the attributes have been set
        super().__init__(type=self.TYPE_DEPTH, **kwargs)

    @property
    def datum(self) -> str:
        """The reference coordinate system. Use constants prefixed with `DATUM_`"""
        return self._datum

    @datum.setter
    def datum(self, value: str):
        self._datum = value


class HorizontalCoordinate(Base):
    """Generic XY coordinates for a point on earth (https://www.fgdc.gov/csdgmgraphical/spref.htm)"""

    #: World Geodetic System 1984 (WGS84)
    DATUM_WGS84 = "WGS84"

    #: North American Datum of 1983 (NAD 83)
    DATUM_NAD83 = "NAD83"

    #: North American Datum 1927 (NAD27)
    DATUM_NAD27 = "NAD27"

    #: The quantities of latitude and longitude which define the position of a
    #: point on the Earth's surface with respect to a reference spheroid.
    TYPE_GEOGRAPHIC = "GEOGRAPHIC"

    #: T plane-rectangular coordinate system usually based on, and
    #: mathematically adjusted to, a map projection so that geographic
    #: positions can be readily transformed to and from plane coordinates.
    TYPE_PLANAR_GRID = "PLANAR_GRID"

    #: Any right-handed planar coordinate system of which the z-axis
    #: coincides with a plumb line through the origin that locally is aligned with the surface of the Earth.
    TYPE_PLANAR_LOCAL = "PLANAR_LOCAL"

    #: The systematic representation of all or part of the surface of the Earth on a plane or developable surface.
    TYPE_PLANAR_MAP_PROJECTION = "PLANAR_MAP_PROJECTION"

    #: A description of any coordinate system that is not aligned with the surface of the Earth.
    TYPE_LOCAL = "LOCAL"

    def __init__(self, **kwargs):
        self._x: float = None
        self._y: float = None
        self._datum: str = None
        self._type: str = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)

    @property
    def x(self) -> float:
        """X Coordinate"""
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = value

    @property
    def y(self) -> float:
        """Y Coordinate"""
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = value

    @property
    def datum(self) -> str:
        """The reference coordinate system. Use constants prefixed with `DATUM_`"""
        return self._datum

    @datum.setter
    def datum(self, value: str):
        self._datum = value

    @property
    def type(self) -> str:
        """The type of horizontal coordinates. Use constants prefixed with `TYPE_`"""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value


class GeographicCoordinate(HorizontalCoordinate):
    """
    The latitude and longitude which define the position of a point on
    the Earth's surface with respect to a reference spheroid.
    (https://www.fgdc.gov/csdgmgraphical/spref.htm)\
    """

    #: Decimal degrees
    UNITS_DEC_DEGREES = "DD"

    #: Decimal minutes
    UNITS_DEC_MINUTES = "DM"

    #: Decimal seconds
    UNITS_DEC_SECONDS = "DS"

    #: Degrees and decimal minutes
    UNITS_DEGREES_DEC_MINUTES = "DDM"

    #: Degrees, minutes, and decimal second
    UNITS_DEGREES_MIN_DEC_SECS = "DMDS"

    #: Radians
    UNITS_RADIANS = "Radians"

    #: Grads
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
        self._units: str = None

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
    def latitude(self) -> float:
        """Alias for Y Coordinate"""
        return self.y

    @property
    def longitude(self) -> float:
        """Alias for X Coordinate"""
        return self.x

    @property
    def units(self) -> str:
        """Latitude and longitude units. Use constants prefixed with `UNTIS_`"""
        return self._units

    @units.setter
    def units(self, value: str):
        self._units = value


class Feature(Base):
    """
    A general feature upon which an observation can be made. Loosely after GF_Feature (ISO).
    """

    def __init__(self, datasource, **kwargs):
        self._id: str = None
        self._name: str = None
        self._description: str = None
        self._feature_type: str = None
        self._observed_property_variables: List[str] = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

        if self.observed_property_variables and isinstance(self.observed_property_variables, (tuple, list, enumerate)):
            # synthesize measurement variables
            synth_params = []
            for synth_param in get_datasource_observed_property_variables(datasource, self.observed_property_variables):
                synth_params.append(synth_param.observed_property_variable_id)

            self.observed_property_variables = synth_params

        elif self.observed_property_variables:
            self.observed_property_variables = [self.observed_property_variables]

    def __validate__(self):
        """
        Validate attributes
        """

        if self.feature_type is not None and self.feature_type not in FeatureTypes.TYPES.keys():
            raise AttributeError("Feature attr feature_type must be FeatureTypes.")

    @property
    def id(self) -> str:
        """Unique identifier for the feature"""
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def name(self) -> str:
        """A name for the feature"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        """The feature description"""
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def feature_type(self) -> str:
        """The feature type. For a list of feature types see :class:`basin3d.models.FeatureTypes`."""
        return self._feature_type

    @feature_type.setter
    def feature_type(self, value: str):
        self._feature_type = value

    @property
    def observed_property_variables(self) -> List[str]:
        """List of observed property variables"""
        return self._observed_property_variables

    @observed_property_variables.setter
    def observed_property_variables(self, value: List[str]):
        self._observed_property_variables = value


class SamplingFeature(Feature):
    """
    A feature where sampling is conducted. OGC Observation & Measurements SF_SamplingFeature.
    """

    def __init__(self, datasource, **kwargs):
        self._related_sampling_feature_complex: List[SamplingFeature] = []

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
        self.__validate__()

    # ToDo: validate items in lists
    def __validate__(self):
        if not isinstance(self.related_sampling_feature_complex, (list, tuple, set)):  # check for better not iterable
            self.related_sampling_feature_complex = [self.related_sampling_feature_complex]

    @property
    def related_sampling_feature_complex(self) -> List['SamplingFeature']:
        """List of related sampling features
           obj :class:`RelatedSamplingFeature`"""
        return self._related_sampling_feature_complex

    @related_sampling_feature_complex.setter
    def related_sampling_feature_complex(self, value: List['SamplingFeature']):
        self._related_sampling_feature_complex = value


class SpatialSamplingFeature(SamplingFeature):
    """
    A spatially-defined feature where sampling is conducted. OGC Observation & Measurements SF_SpatialSamplingFeature.
    """

    def __init__(self, datasource, **kwargs):
        self._shape: str = None
        self._coordinates: Coordinate = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
        self.__validate__()

        # Set the shape dependent on feature_type
        for key, values in FeatureTypes.SHAPE_TYPES.items():
            if self.feature_type in values:
                self.shape = key

    def __validate__(self):
        """
        Require that feature_type is set
        """

        if self.feature_type is None:
            raise AttributeError("Feature attr feature_type must be indicated")

        if self.coordinates and not isinstance(self.coordinates, Coordinate):
            raise TypeError("coordinates must be Coordinate instance.")

        self._verify_coordinates_match_shape()

    def _verify_coordinates_match_shape(self):
        # Consider: invert logic in so that the coordinates specify the shape.
        error_msg = "Absolute coordinates do not match specified shape {}. ".format(self.shape)
        if self.coordinates and self.coordinates.absolute:
            if self.shape == SpatialSamplingShapes.SHAPE_POINT:
                if len(self.coordinates.absolute.horizontal_position) != 1:
                    raise AttributeError(error_msg + "Shape {} must have only one point."
                                         .format(SpatialSamplingShapes.SHAPE_POINT))
                else:
                    return
            if self.shape == SpatialSamplingShapes.SHAPE_SURFACE:
                if len(self.coordinates.absolute.horizontal_position) < 1 or \
                        self.coordinates.absolute.horizontal_position[0].x != \
                        self.coordinates.absolute.horizontal_position[-1].x or \
                        self.coordinates.absolute.horizontal_position[0].y != \
                        self.coordinates.absolute.horizontal_position[-1].y:
                    raise AttributeError(error_msg + "Shape {} must have more than one point. "
                                                     "The first and last points in the list must "
                                                     "be the same point.".format(SpatialSamplingShapes.SHAPE_SURFACE))
                else:
                    return
            if self.shape == SpatialSamplingShapes.SHAPE_CURVE:
                if len(self.coordinates.absolute.horizontal_position) < 1 or (
                        self.coordinates.absolute.horizontal_position[0].x ==
                        self.coordinates.absolute.horizontal_position[-1].x and
                        self.coordinates.absolute.horizontal_position[0].y ==
                        self.coordinates.absolute.horizontal_position[-1].y):
                    raise AttributeError(error_msg + "Shape {} must have more than one point. "
                                                     "The first and last points in the list must "
                                                     "NOT be the same point.".format(SpatialSamplingShapes.SHAPE_CURVE))
                else:
                    return
            # ToDo: distinguish solid from curve when altitude is included

    @property
    def coordinates(self) -> Coordinate:
        """Description of feature location. An instance of :class:`Coordinate`"""
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value: Coordinate):
        self._coordinates = value

    @property
    def shape(self) -> str:
        """The shape of the feature. See :class:`basin3d.models.SpatialSamplingShapes`"""
        return self._shape

    @shape.setter
    def shape(self, value: str):
        self._shape = value


class MonitoringFeature(SpatialSamplingFeature):
    """
    A feature upon which monitoring is made. OGC Timeseries Profile OM_MonitoringFeature.
    """

    def __init__(self, datasource, **kwargs):
        self._description_reference: str = None
        self._related_party = []
        self._utc_offset: int = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    @property
    def description_reference(self) -> str:
        """Extra information about the Monitoring Feature"""
        return self._description_reference

    @description_reference.setter
    def description_reference(self, value):
        self._description_reference = value

    @property
    def related_party(self) -> List[Person]:
        """list of Person, people or organizations responsible for Feature.
           To be extended in future to full OGC Responsible_Party"""
        return self._related_party

    @related_party.setter
    def related_party(self, value: List[Person]):
        self._related_party = value

    @property
    def utc_offset(self) -> int:
        """Coordinated Universal Time (UTC) offset in hours (e.g. +/-9)"""
        return self._utc_offset

    @utc_offset.setter
    def utc_offset(self, value: int):
        self._utc_offset = value
