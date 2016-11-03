from django.contrib import admin
from django.contrib.admin import ModelAdmin

from basin3d.models import DataSource, MeasurementVariable, DataSourceMeasurementVariable


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin','location')


@admin.register(MeasurementVariable)
class ParamterAdmin(ModelAdmin):
    list_display = ('name','broker_id','primary_category')


@admin.register(DataSourceMeasurementVariable)
class DataSourceMeasurementVariableAdmin(ModelAdmin):
    list_display = ('name', 'datasource', 'measure_variable')
