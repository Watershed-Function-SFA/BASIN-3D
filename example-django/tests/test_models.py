
from django.test import TestCase

from basin3d.models import DataSource, SamplingMedium, MeasurementVariable, \
    ObservedPropertyVariable, ObservedProperty, DataSourceObservedPropertyVariable


class DataSourceTestCase(TestCase):
    def setUp(self):
        DataSource.objects.create(name="Foo", plugin_module="foo.bar.plugins", plugin_class="Baz", id_prefix="F")
        DataSource.objects.create(name="Bar", plugin_module="foo.plugins", plugin_class="Bar", id_prefix="B")

    def test_get(self):
        """Assert that the Data Sources were created"""
        foo = DataSource.objects.get(name="Foo")
        bar = DataSource.objects.get(name="Bar")
        self.assertEqual(bar.name, "Bar")
        self.assertEqual(foo.name, 'Foo')


class ObservedPropertyTestCase(TestCase):
    """
    Assert that the parameters are created
    """
    def setUp(self):
        """
        Load some fake data to use in the tests
        """
        self.datasource = DataSource.objects.get(name="Alpha")
        self.observed_property_var = ObservedPropertyVariable(
            id="FOO", full_name="Groundwater Flux",
            categories="Hydrology,Subsurface")
        self.sampling_medium = SamplingMedium()

    def test_observed_property_create(self):
        """ Was the object created correctly? """

        obj = ObservedProperty(description="Acetate (CH3COO)",
                               observed_property_variable=self.observed_property_var,
                               sampling_medium=self.sampling_medium,
                               datasource=self.datasource)

        assert obj.description == "Acetate (CH3COO)"
        assert obj.observed_property_variable == self.observed_property_var
        assert obj.sampling_medium == self.sampling_medium
        assert obj.datasource == self.datasource

    def test_observed_property_variable_create(self):
        """ create the object and test attributes """

        assert self.observed_property_var.id == "FOO"
        assert self.observed_property_var.full_name == "Groundwater Flux"
        assert self.observed_property_var.categories == "Hydrology,Subsurface"

    def test_datasource_observed_property_variable_create(self):
        """ Was the object created correctly? """
        obj = DataSourceObservedPropertyVariable(
            datasource=self.datasource, observed_property_variable=self.observed_property_var,
            name="Alpha")

        assert obj.datasource == self.datasource
        assert obj.observed_property_variable == self.observed_property_var
        assert obj.name == "Alpha"


class ParameterTestCase(TestCase):  # Delete
    """
    Assert that the parameters are created
    """
    def setUp(self):
        """
        Load some fake data to use in the tests
        """
        MeasurementVariable.objects.create(id="FOO",
                                           full_name="Groundwater Flux",
                                           categories="Hydrology,Subsurface")

    def test_get(self):
        """ Was the object created correctly? """
        obj = MeasurementVariable.objects.get(id="FOO")
        self.assertEqual(obj.full_name, "Groundwater Flux")
        self.assertEqual(obj.categories, "Hydrology,Subsurface")
