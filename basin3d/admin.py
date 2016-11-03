from django.contrib import admin
from django.contrib.admin import ModelAdmin

from basin3d.models import DataSource, MeasurementVariable, DataSourceMeasurementVariable


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin','location')
    fields = ('name', 'location', 'plugin')
    readonly_fields = ('name', 'plugin',)
    actions = None


@admin.register(MeasurementVariable)
class MeasurementVariableAdmin(ModelAdmin):
    list_display = ('name','broker_id','primary_category')

    actions = None


@admin.register(DataSourceMeasurementVariable)
class DataSourceMeasurementVariableAdmin(ModelAdmin):
    list_display = ('name', 'datasource', 'measure_variable')
