from basin3d.models import DataSource, MeasurementVariable, DataSourceMeasurementVariable, \
    Measurement, SamplingMedium
from django.contrib import admin
from django.contrib.admin import ModelAdmin


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin','location')
    fields = ('name', 'location', 'plugin','id_prefix',)
    readonly_fields = ('name', 'id_prefix', 'plugin')
    actions = None


@admin.register(MeasurementVariable)
class MeasurementVariableAdmin(ModelAdmin):
    list_display = ('id','full_name','categories')

    actions = None


@admin.register(DataSourceMeasurementVariable)
class DataSourceMeasurementVariableAdmin(ModelAdmin):
    list_display = ('name', 'datasource', 'measure_variable')
    list_filter = ('datasource', 'measure_variable')


@admin.register(Measurement)
class DataSourceMeasurementAdmin(ModelAdmin):
    list_display = ('variable', 'datasource', 'sampling_medium')
    readonly_fields = ('datasource', 'variable')
    list_filter = ('datasource', 'sampling_medium')


@admin.register(SamplingMedium)
class SamplingMediumAdmin(ModelAdmin):
    list_display = ('name', 'description')

