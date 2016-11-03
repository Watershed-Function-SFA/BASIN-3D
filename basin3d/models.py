from __future__ import unicode_literals

from django.db import models
from django_extensions.db.fields.encrypted import EncryptedTextField
from djangoplugins.fields import PluginField

from basin3d.plugins import BrokerSourcePluginPoint


class DataSource(models.Model):
    """
    Data Source  definition
    """
    name = models.CharField(max_length=20, unique=True, blank=False)
    location = models.TextField(blank=True)
    plugin = PluginField(BrokerSourcePluginPoint, blank=True)
    credentials = EncryptedTextField(blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<DataSource %r>' % (self.name)


class MeasurementVariable(models.Model):
    """
    Broker Parameter Definitions

    """

    # Unique string Identifier for the Broker Parameter
    broker_id = models.CharField(max_length=50, unique=True, blank=False)

    # Long name of the Broker Parameters
    name = models.CharField(max_length=255, blank=False)

    # Unit of measurement
    unit = models.CharField(max_length=100)

    # Primary Category of the parameter
    primary_category = models.CharField(max_length=100)

    # Secondary Category of the parameter
    secondary_category = models.CharField(max_length=100)

    class Meta:
        ordering = ('broker_id',)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<MeasurementVariable {}>".format(self.broker_id)


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
