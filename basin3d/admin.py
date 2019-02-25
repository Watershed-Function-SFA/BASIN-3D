from basin3d.models import DataSource, \
    ObservedProperty, ObservedPropertyVariable, DataSourceObservedPropertyVariable, \
    MeasurementVariable, DataSourceMeasurementVariable, Measurement, SamplingMedium
from django.contrib import admin
from django.contrib.admin import ModelAdmin


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'plugin_module','plugin_class','location')
    fields = ('name', 'location', 'plugin_module','plugin_class','id_prefix',)
    readonly_fields = ('name', 'id_prefix', 'plugin_module','plugin_class')
    actions = None


@admin.register(ObservedPropertyVariable)
class ObservedPropertyVariableAdmin(ModelAdmin):
    list_display = ('id', 'full_name', 'categories')

    actions = None


@admin.register(DataSourceObservedPropertyVariable)
class DataSourceObservedPropertyVariableAdmin(ModelAdmin):
    list_display = ('name', 'datasource', 'observed_property_variable')
    list_filter = ('datasource', 'observed_property_variable')


@admin.register(ObservedProperty)
class ObservedPropertyAdmin(ModelAdmin):
    list_display = ('observed_property_variable', 'datasource', 'sampling_medium')
    readonly_fields = ('datasource', 'observed_property_variable')
    list_filter = ('datasource', 'sampling_medium')


@admin.register(MeasurementVariable)
class MeasurementVariableAdmin(ModelAdmin):
    list_display = ('id', 'full_name', 'categories')

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

