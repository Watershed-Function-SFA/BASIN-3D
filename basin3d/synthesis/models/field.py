"""
`basin3d.synthesis.models.field`
********************************

.. currentmodule:: basin3d.synthesis.models.field

:synopsis: Classes to represent Multi-scale Spatial Hierarchy for Field Observations

* :class:`Coordinates` - Generic XYZ coordinates for a point on earth
* :class:`MeasurementPosition` - Sublocation within a point location
* :class:`Plot` -  A group of related point measurements
* :class:`PointLocation` - A point on the earth where something is being measured
* :class:`Region` - An arbitrary area
* :class:`SamplingFeature` - Base class.  A feature where sampling is conducted.
* :class:`Site` - A demarcated, geographic area where measurements are being conducted.

"""

from basin3d.synthesis.models import Base


class Coordinates(Base):
    """Generic XYZ coordinates for a point on earth

    Attributes:
        latitude
        longitude
        spatial_ref_system,
        elevation
        elevation_ref_system
    """

    SPATIAL_REF_WGS84 = "WGS84"
    SPATIAL_REF_GGRS87 = "GGRS87"
    SPATIAL_REF_NAD83 = "NAD83"
    SPATIAL_REF_NAD27 = "NAD27"

    def __init__(self, **kwargs):
        self.latitude = None
        self.longitude = None
        self.spatial_ref_system = None
        self.elevation = None
        self.elevation_ref_system = None

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)


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
        *coordinates:* Coordinates
        *position:* :class:`MeasurementPosition`
    """

    def __init__(self, datasource, **kwargs):
        self.site_id = None
        self.geographical_group_id = None
        self.geographical_group_type = None
        self.coordinates = None
        self.position = None

        # Initialize after the attributes have been set
        super().__init__(datasource, datasource_ids=['site_id', 'geographical_group_id'], **kwargs)


class MeasurementPosition(Base):
    """(MAYBE THIS SHOULD BE SPECIFIC TYPES OF MEASUREMENT POSITIONS.. WELL MEASUREMENT,
    TOWER SENSORS, TREE PROBES - NEED DIFFERENT INFO)

    Sublocation within a point location - depth, sensors around a tree.
    Adopted from Danielle’s metadata framework.

    Attributes:
        *type:* enum (“Point3D?”)
        *depth_height:* float (+ve for height, -ve for depth)
        *depth_height_units:* string
    """

    def __init__(self, **kwargs):
        self.depth_height = None
        self.depth_height_units = None
        self.type = "point-3d"

        # Initialize after the attributes have been set
        super().__init__(None, **kwargs)
