
from django.test import TestCase

from basin3d.models import DataSource, MeasurementVariable


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


class ParameterTestCase(TestCase):
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

