"""
`basin3d.models`
****************

.. currentmodule:: basin3d.models

:synopsis: The BASIN-3D  Models
:module author: Val Hendrix <vhendrix@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top


"""
from __future__ import unicode_literals
from django.db import models
from django_extensions.db.fields.encrypted import EncryptedTextField
from importlib import import_module


class SpatialSamplingShapes(object):
    """
    GM_Shape defined in OGC O&M
    """

    SHAPE_SOLID = "Solid"
    SHAPE_SURFACE = "Surface"
    SHAPE_CURVE = "Curve"
    SHAPE_POINT = "Point"


class FeatureTypes(object):
    """
    Feature Types where an Observation can be made.

    This is a controlled CV list that we are maintaining. USGS Watershed Boundry Dataset is used.
    We're trying to strike a balance between commonly used hierarchical levels and features
    versus a runaway list of Feature types. OGC O&M suggests that Features should be
    determined as needed.
    """

    REGION = 0
    SUBREGION = 1
    BASIN = 2
    SUBBASIN = 3
    WATERSHED = 4
    SUBWATERSHED = 5
    SITE = 6
    PLOT = 7
    HORIZONTAL_PATH = 8  # Rivers, Transects
    VERTICAL_PATH = 9  # Towers, Boreholes, Trees, Pits
    POINT = 10

    TYPES = {
        REGION: "Region",
        SUBREGION: "Subregion",
        BASIN: "Basin",
        SUBBASIN: "Subbasin",
        WATERSHED: "Watershed",
        SUBWATERSHED: "Subwatershed",
        SITE: "Site",
        PLOT: "Plot",
        HORIZONTAL_PATH: "Horizontal Path",
        VERTICAL_PATH: "Vertical Path",
        POINT: "Point"
    }

    SHAPE_TYPES = {
        SpatialSamplingShapes.SHAPE_POINT: [POINT],
        SpatialSamplingShapes.SHAPE_CURVE: [HORIZONTAL_PATH, VERTICAL_PATH],
        SpatialSamplingShapes.SHAPE_SURFACE: [REGION, SUBREGION, BASIN, SUBBASIN, WATERSHED,
                               SUBWATERSHED, SITE, PLOT],
        SpatialSamplingShapes.SHAPE_SOLID: []
    }


def get_feature_types():
    """ Helper function for FeatureTypes """
    return [x for x in FeatureTypes.TYPES.values()]


class StringListField(models.TextField):
    """
    StringListField stored delimited strings in the database.

    :param: delimiter
    :type: str
    """

    def __init__(self, *args, **kwargs):
        self.delimiter = ","
        if "delimiter" in kwargs.keys():
            self.delimiter = kwargs["delimiter"]

        super(StringListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list) or isinstance(value, tuple):
            return value
        elif isinstance(value, str):
            return value.split(self.delimiter)

        raise ValueError("ListField must be  delimited string")

    def get_prep_value(self, value):
        if value is None:
            return value
        else:
            return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_db_prep_value(value, None)


class DataSource(models.Model):
    """
    Data Source definition
    """
    name = models.CharField(max_length=20, unique=True, blank=False)
    id_prefix = models.CharField(max_length=5, unique=True, blank=False)
    location = models.TextField(blank=True)
    plugin_module = models.TextField(blank=True)
    plugin_class = models.TextField(blank=True)
    credentials = EncryptedTextField(blank=True)
    enabled = models.BooleanField(default=True)


    class Meta:
        ordering = ['id_prefix']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSource %r>' % (self.name)

    def get_plugin(self):
        """
        Return the plugin
        :return:
        """

        module = import_module(self.plugin_module)
        plugin_class = getattr(module, self.plugin_class)
        return plugin_class()


class ObservedProperty(models.Model):
    """
    Defining the attributes for a single/multiple Observed Properties

    Attributes:
        - *id:* string, (Cs137 MID)
        - *description:* id, Cs 137 air dose rate car survey campaigns
        - *observed_property_variable_id:* string, Cs137MVID
        - *sampling_medium:* enum (water, gas, solid phase, other, not applicable)
        - *owner:* Person (optional), NotImplemented
        - *contact:* Person (optional), NotImplemented
    """

    description = models.TextField(null=True, blank=True)
    observed_property_variable = models.ForeignKey('ObservedPropertyVariable', null=False, on_delete=models.CASCADE)
    sampling_medium = models.ForeignKey('SamplingMedium', null=False, on_delete=models.CASCADE)
    datasource = models.ForeignKey('DataSource', null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('observed_property_variable', 'datasource')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.description

    def __repr__(self):
        return '<ObservedProperty %r>' % (self.description)


class ObservedPropertyVariable(models.Model):
    """
    Defining the properties being observed (measured). See http://vocabulary.odm2.org/variablename/ for controlled vocabulary

        Attributes:
            - *id:* string,
            - *full_name:* string,
            - *abbreviation:* string,
            - *categories:* Array of strings (in order of priority).

    See http://vocabulary.odm2.org/variabletype/ for options, although I think we should have our own list (theirs is a bit funky).


    """

    # Unique string Identifier for the Observed Property Variable
    id = models.CharField(max_length=50, unique=True, blank=False, primary_key=True)

    # Long name of the Observed Property Variable
    full_name = models.CharField(max_length=255)

    # Ordered list of categories
    categories = StringListField(blank=True, null=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.full_name

    def __repr__(self):
        return "<ObservedPropertyVariable {}>".format(self.id)


class DataSourceObservedPropertyVariable(models.Model):
    """
    Synthesis of Data Source Parameters with Broker parameters
    """
    datasource = models.ForeignKey(DataSource, related_name='basin3d_datasource', on_delete=models.CASCADE)
    observed_property_variable = models.ForeignKey(ObservedPropertyVariable,
                                                   related_name='basin3d_observedpropertyvariable',
                                                   on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False)

    class Meta:
        unique_together = (("datasource", "observed_property_variable"),)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSourceObservedPropertyVariable %r>' % (self.name)


class SamplingMedium(models.Model):
    """
    Types of sampling mediums for Observed Properties
    """

    SOLID_PHASE = "solid phase"
    WATER = "water"
    GAS = "gas"
    OTHER = 'other'
    NOT_APPLICABLE = 'N/A'
    SAMPLING_MEDIUMS = [WATER, GAS, SOLID_PHASE, OTHER, NOT_APPLICABLE]

    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<SamplingMedium %r>' % (self.name)
