from django.test import TestCase

from basin3d.models import DataSource, MeasurementVariable


class DataSourceTestCase(TestCase):
    def setUp(self):
        DataSource.objects.create(name="Foo",plugin_id=1)
        DataSource.objects.create(name="Bar",plugin_id=1)

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
        MeasurementVariable.objects.create(broker_id="FOO",
                                           name="Groundwater Flux",
                                           unit='',
                                           primary_category="Hydrology",
                                           secondary_category="Subsurface")

    def test_get(self):
        """ Was the object created correctly? """
        obj = MeasurementVariable.objects.get(broker_id="FOO")
        self.assertEqual(obj.name, "Groundwater Flux")
        self.assertEqual(obj.unit, "")
        self.assertEqual(obj.primary_category, "Hydrology")
        self.assertEqual(obj.secondary_category, "Subsurface")

