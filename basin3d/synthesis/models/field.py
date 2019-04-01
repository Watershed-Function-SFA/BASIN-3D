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
* :class:`SamplingFeature` - Base class.  A feature where sampling is conducted  #ToDo: edit
* :class:`VerticalCoordinate` - The reference frame or system from which vertical distances (altitudes or depths) are measured.
# ToDo: add new documentation

"""
from basin3d.plugins import get_datasource_observed_property_variables
from basin3d.synthesis.models import Base, Person  # pass Person for plugins
from basin3d.models import FeatureTypes, SpatialSamplingShapes


class RelatedSamplingFeature(Base):
    """
    Class that represents a related sampling feature and it's role relative to
    the sampling feature to which it is related.

    See OGC Observations and Measurements
    """

    ROLE_PARENT = "Parent"

    ROLE_TYPES = [ROLE_PARENT]

    def __init__(self, datasource, **kwargs):
        self.related_sampling_feature = None
        self.related_sampling_feature_type = None
        self.role = None

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
            print(self.related_sampling_feature_type.__class__)
            raise AttributeError("RelatedSamplingFeature related_sampling_feature_type must be FeatureTypes")

        if self.role is None:
            raise AttributeError("RelatedSamplingFeature role is required.")
        elif self.role not in RelatedSamplingFeature.ROLE_TYPES:
            raise AttributeError("RelatedSamplingFeature role must be one of predefined roles.")


class Coordinate(Base):
    """
    Top level coordinate class that holds absolute or relative coordinates

    Attributes:
        *absolute:* obj AbsoluteCooradinate
        *representative:* obj RepresentativeCoordinate
    """

    def __init__(self, **kwargs):
        self.absolute = None
        self.representative = None

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
        if self.absolute is None:
            if self.representative.representative_point is None:
                raise AttributeError("Representative_point is required if only representative coordinates are provided.")


class AbsoluteCoordinate(Base):
    """
    Absolute coordinate class.

    Planned extension to better check point, curve, surface, solid shape-specific coordinates.
    May want to include a type attribute akin to GeoJSON type
    In future, reconsider the format of attributes to allow for more types of description (meshes, solids, etc)

    Attributes:
        *horizontal_position:* list of obj GeographicCoordinate
        *vertical_extent:* list of obj AltitudeCoordinate
        *shape:* str internally determined by coordinates (determination of solid not functional)
    """

    def __init__(self, **kwargs):
        self.horizontal_position = []
        self.vertical_extent = []

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
        self.__validate__()

    def __validate__(self):
        # ToDo: require horizontal position
        if self.horizontal_position is None:
            raise AttributeError("Horizontal position required for AbsoluteCoordinate instance")
        elif not isinstance(self.horizontal_position, (list, tuple, set)):  # check for better not iterable
            self.horizontal_position = [self.horizontal_position]

        if not isinstance(self.vertical_extent, (list, tuple, set)):
            self.vertical_extent = [self.vertical_extent]

        # ToDo: validate obj types
        for obj in self.horizontal_position:
            if not isinstance(obj, GeographicCoordinate):
                raise TypeError("Horizontal position must be instance of GeographicCoordinate")

        if self.vertical_extent is not None:
            for obj in self.vertical_extent:
                if not isinstance(obj, AltitudeCoordinate):
                    raise TypeError("Vertical extent must be instance of AltitudeCoordinate")

        if len(self.horizontal_position) != len(self.vertical_extent):
            raise AttributeError("Lengths of horizontal positions and vertical extent must be equal.")

        # ToDo: add validation for shape coordinates.


class RepresentativeCoordinate(Base):
    """
    Representative coordinates

    Extendable to other forms of representing (e.g., diameter, area, side_length)
    Representative point types are also expandable as use cases require.

    Attributes:
        *representative_point:* obj AbsoluteCoordinate for POINT
        *representative_point_type:* string (CV assumes @ local surface)
        *vertical_position:* obj DepthCoordinate
    """

    REPRESENTATIVE_POINT_TYPE_CENTER_LOCAL_SURFACE = "Center Local Surface"
    REPRESENTATIVE_POINT_TYPE_UPPER_LEFT_CORNER = "Upper Left Corner"
    REPRESENTATIVE_POINT_TYPE_UPPER_RIGHT_CORNER = "Upper Right Corner"
    REPRESENTATIVE_POINT_TYPE_LOWER_LEFT_CORNER = "Lower Left Corner"
    REPRESENTATIVE_POINT_TYPE_LOWER_RIGHT_CORNER = "Lower Right Corner"

    def __init__(self, **kwargs):
        self.representative_point = None
        self.representative_point_type = None
        self.vertical_position = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
        self.__validate__()

    def __validate__(self):
        """
        Validate attributes
        """

        # if representative point, require representative point type
        if self.representative_point is not None:
            if self.representative_point_type is None:
                raise AttributeError("representative_point_type is required if representative_point provided.")


class VerticalCoordinate(Base):
    """
    The reference frame or system from which vertical distances (altitudes or depths) are measured.

    Attributes:
        *type:* enum ("altitude”, "depth),
        *value:* float,
        *datum:* string,
        *resolution:* float, the minimum distance possible between two adjacent
                      depth values, expressed in Depth Distance Units of measure
        *distance_units:* enum  ("meters", "feet"), the means used to encode depths.
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
        self.resolution = None
        self.distance_units = None
        self.encoding_method = None
        self.datum = None
        self.type = None

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
        return self.y

    @property
    def longitude(self):
        return self.x


class Feature(Base):
    """
    A general feature upon which an observation can be made. Loosely after GF_Feature (ISO).

    Inherited attributes (:class:`Base`):
        - *datasource*: string

    Attributes:
        - *id:* string
        - *name:* string
        - *description:* string
        - *feature_type:* string
        - *observed_property_variables:* list
    """

    def __init__(self, datasource, **kwargs):
        self.id = None
        self.name = None
        self.description = None
        self.feature_type = None
        self.observed_property_variables = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

        if self.observed_property_variables and isinstance(self.observed_property_variables, (tuple, list, enumerate)):
            # synthesize measurement variables
            synth_params = []
            for synth_param in get_datasource_observed_property_variables(datasource, self.observed_property_variables):
                synth_params.append(synth_param.observed_property_variable_id)

            self.observed_property_variables = synth_params

    def __validate__(self):
        """
        Validate attributes
        """

        if self.feature_type is not None and self.feature_type not in FeatureTypes.TYPES.keys():
            raise AttributeError("Feature attr feature_type must be FeatureTypes.")


class SamplingFeature(Feature):
    """
    A feature where sampling is conducted. OGC Observation & Measurements SF_SamplingFeature.

    Inherited attributes (:class:`Base`):
        - *datasource*: string

    Inherited attributes (:class:`Feature):
        - *id:* string
        - *name:* string
        - *description:* string
        - *feature_type:* string
        - *observed_property_variables:* list

    Attributes:
        - *related_sampling_feature_complex:* list

    Possible extension: sampled_feature(s)
    """

    def __init__(self, datasource, **kwargs):
        self.related_sampling_feature_complex = []

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)

    # ToDo: validate items in lists


class SpatialSamplingFeature(SamplingFeature):
    """
    A feature where sampling is conducted. OGC Observation & Measurements SF_SpatialSamplingFeature.

    Inherited attributes (:class:`Base`):
        - *datasource*: string

    Inherited attributes (:class:`Feature`):
        - *id:* string
        - *name:* string
        - *description:* string
        - *feature_type:* string
        - *observed_property_variable_complex:* list

    Inherited attributes (:class:`SamplingFeature`):
        - *related_sampling_feature_complex:* list

    Attributes:
        - *shape:* string
        - *coordinates:* Coordinate instance
    """

    def __init__(self, datasource, **kwargs):
        self.shape = None
        self.coordinates = None

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
        if self.coordinates.absolute is not None:
            if self.shape == SpatialSamplingShapes.SHAPE_POINT:
                if len(self.coordinates.absolute.horizontal_position) != 1:
                    raise AttributeError(error_msg + "Shape { } must have only one point.")
                else:
                    return
            if self.shape == SpatialSamplingShapes.SHAPE_SURFACE:
                if len(self.coordinates.absolute.horizontal_position) < 1 or \
                        self.coordinates.absolute.horizontal_position[0] != \
                        self.coordinates.absolute.horizontal_position[-1]:
                    raise AttributeError(error_msg + "Shape { } must have more than one point. "
                                                     "The first and last points in the list must "
                                                     "be the same point.")
                else:
                    return
            if self.shape == SpatialSamplingShapes.SHAPE_CURVE:
                if len(self.coordinates.absolute.horizontal_position) < 1 or \
                        self.coordinates.absolute.horizontal_position[0] == \
                        self.coordinates.absolute.horizontal_position[-1]:
                    raise AttributeError(error_msg + "Shape { } must have more than one point. "
                                                     "The first and last points in the list must "
                                                     "NOT be the same point.")
                else:
                    return
            # ToDo: distinguish solid from curve when altitude is included


class MonitoringFeature(SpatialSamplingFeature):
    """
    A feature where monitoring is happenin. OGC Timeseries Profile OM_MonitoringFeature.

    Inherited attributes (:class:`Base`):
        - *datasource*: string

    Inherited attributes (:class:`Feature`):
        - *id:* string
        - *name:* string
        - *description:* string
        - *feature_type:* string
        - *observed_property_variables:* list

    Inherited attributes (:class:`SamplingFeature`):
        - *related_sampling_feature_complex:* list

    Inherited attributes (:class:`SpatialSamplingFeature`):
        - *shape:* string
        - *coordinates:* Coordinate instance

    Attributes:
        - *description_reference:* string  # extra information about the Monitoring Feature
        - *related_party:* list of obj Person  # extend in future to full OGC Responsible_Party
        - *utc_offset:* int

    """

    def __init__(self, datasource, **kwargs):
        self.description_reference = None
        self.related_party = []
        self.utc_offset = None

        # Initialize after the attributes have been set
        super().__init__(datasource, **kwargs)
