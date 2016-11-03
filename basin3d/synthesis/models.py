class Site(object):
    """
     A specific area where measurements are being collected.

    """
    __attributes = {'site_id', 'name', 'country',
                    'state_province',
                    'geom',
                    'contact_name',
                    'contact_email',
                    'contact_institution',
                    'urls'}

    def __init__(self, **kwargs):

        self.site_id = None
        self.name = None
        self.country = None
        self.state_province = None
        self.geom = None
        self.contact_name = None
        self.contact_email = None
        self.contact_institution = None
        self.urls = []
        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        if len(kwargs.keys()) > 0  and Site.__attributes.isdisjoint(set(kwargs.keys())):
            bad_attributes = set(kwargs.keys()).difference(Site.__attributes)
            raise ValueError("Invalid argument(s) for Sites: {}".format(bad_attributes))

        self.__dict__.update(kwargs)


class Location(object):
    """
    A specific point (lat/long) where repeat measurements are being made.
    All man-made locations (tower, crane, weather station, well pit) could be
    lumped into one location type - with different levels. Above ground structures
    can have positive levels (heights),
    below ground structures can have negative levels (depths)

    """
    __attributes = {'location_id'
                    'data_source_id',
                    'name',
                    'group',
                    'type',
                    'geom'  # (e.g lat,lon,elevation)
                    'measure_variables'
                    }

    def __init__(self, **kwargs):
        self.site_id = None
        self.location_id = None
        self.name=None
        self.group = None
        self.type = None
        self.geom = None
        self.measure_variables = []

        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        if len(kwargs.keys()) > 0 and Location.__attributes.isdisjoint(set(kwargs.keys())):
            bad_attributes = set(kwargs.keys()).difference(Location.__attributes)
            raise ValueError("Invalid argument(s) for Sites: {}".format(bad_attributes))

        self.__dict__.update(kwargs)


class DataPoint(object):
    """

    var bDataPoint = function (type, parameter, location, depth, timestamp, value, unit, average, source) {
    this.type = type;
    this.parameter = parameter;
    this.location = location; //Defines X,Y
    this.depth = depth; //Defines Z
    this.timestamp = timestamp; //Defines T
    this.value = value;
    this.unit = unit;
    this.average=average;
    this.source = source;
};
    """
    __attributes = {'type',
                    'parameter_id'
                    'location_id',
                    'site_id',
                    'depth',
                    'timestamp',
                    'value',
                    'unit'
                    'average'
                    }

    def __init__(self, **kwargs):
        self.type = None
        self.location_id = None
        self.site_id = None
        self.depth = None
        self.timestamp = None
        self.value = None
        self.unit = None
        self.average =None

        if not isinstance(kwargs, dict):
            raise TypeError("Expected a dict")

        if len(kwargs.keys()) > 0 and DataPoint.__attributes.isdisjoint(set(kwargs.keys())):
            bad_attributes = set(kwargs.keys()).difference(DataPoint.__attributes)
            raise ValueError("Invalid argument(s) for DataPoint: {}".format(bad_attributes))

        self.__dict__.update(kwargs)
