from basin3d.models import DataSource, MeasurementVariable, DataSourceMeasurementVariable
from django.contrib import admin
from django.contrib.admin import ModelAdmin


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin','location')
    fields = ('name', 'location', 'plugin')
    readonly_fields = ('name', 'id_prefix', 'plugin')
    actions = None


@admin.register(MeasurementVariable)
class MeasurementVariableAdmin(ModelAdmin):
    list_display = ('id','full_name','categories')

    actions = None


@admin.register(DataSourceMeasurementVariable)
class DataSourceMeasurementVariableAdmin(ModelAdmin):
    list_display = ('name', 'datasource', 'measure_variable')
