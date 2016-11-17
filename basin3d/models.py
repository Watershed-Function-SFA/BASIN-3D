"""
`basin3d.models`
**************************

.. currentmodule:: basin3d.models

:synopsis: The BASIN-3D  Models
:module author: Val Hendrix <vhendrix@lbl.gov>

Database models

* :class:`Base` - The base model class that all synthesis extend from
* :class:`Region` - An arbitrary area

----------------------------------

"""
from __future__ import unicode_literals

from basin3d.plugins import DataSourcePluginPoint
from django.db import models
from django_extensions.db.fields.encrypted import EncryptedTextField
from djangoplugins.fields import PluginField


class StringListField(models.TextField):
    """
    StringListField stored delimited strings in the database.

    :param: delimiter
    :type: str
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self,*args, **kwargs):
        self.delimiter=","
        if "delimiter" in kwargs.keys():
            self.delimiter = kwargs["delimiter"]

        super(StringListField, self).__init__(*args,**kwargs)

    def to_python(self,value):
        if not value:
            value =  []

        if isinstance(value,list) or isinstance(value,tuple):
            return value
        elif isinstance(value,str):
            return value.split(self.delimiter)

        raise ValueError("ListField must be delimited string")

    def get_prep_value(self,value):
        if value is None:
            return value
        else:
            return value

    def value_to_string(self,obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)


class DataSource(models.Model):
    """
    Data Source  definition
    """
    name = models.CharField(max_length=20, unique=True, blank=False)
    id_prefix = models.CharField(max_length=5, unique=True, blank=False)
    location = models.TextField(blank=True)
    plugin = PluginField(DataSourcePluginPoint, blank=True)
    credentials = EncryptedTextField(blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSource %r>' % (self.name)


class MeasurementVariable(models.Model):
    """
    Defining what is being measured. See http://vocabulary.odm2.org/variablename/ for controlled vocabulary

        Attributes:
            - *id:* string,
            - *full_name:* string,
            - *symbol:* string,
            - *categories:* Array of strings (in order of priority).

    See http://vocabulary.odm2.org/variabletype/ for options, although I think we should have our own list (theirs is a bit funky).


    """

    # Unique string Identifier for the Measurement Variable
    id = models.CharField(max_length=50, unique=True, blank=False, primary_key=True)

    # Long name of the Measurement Variable
    full_name = models.CharField(max_length=255)

    # Ordered list of categories
    categories = StringListField(blank=True,null=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.full_name

    def __repr__(self):
        return "<MeasurementVariable {}>".format(self.id)


class DataSourceMeasurementVariable(models.Model):
    """
    Synthesis of Data Source Parameters with Broker parameters
    """
    datasource = models.ForeignKey(DataSource, related_name='basin3d_datasource')
    measure_variable = models.ForeignKey(MeasurementVariable, related_name='basin3d_measurementvariable')
    name = models.CharField(max_length=255, blank=False)

    class Meta:
        unique_together = (("datasource", "measure_variable"),)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSourceMeasurementVariable %r>' % (self.name)
