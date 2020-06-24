import logging

import pytest

from basin3d.plugins import usgs
from django_basin3d.catalog import CatalogDjango
from mybroker import plugins as alpha

log = logging.Logger(__name__)


# ---------------------------------------
# Helper and mock functions

def mock_plugin_get_meta():
    class PluginMeta:
        id = 'Alpha'
        name = 'Alpha'
        location = 'https://asource.foo/'
        id_prefix = 'A'

    return PluginMeta


# ---------------------------------------
# Fixtures


@pytest.fixture
def catalog(monkeypatch):
    from django_basin3d.catalog import CatalogDjango

    catalog = CatalogDjango()
    catalog.plugin_dir = 'mybroker.plugins'

    catalog.initialize([])

    return catalog


# ---------------------------------------
# Tests
# ********* ORDER of tests matters!! see comments
# ********* The catalog is only first created in the test_create_catalog function below.


@pytest.mark.django_db
def test_get_observed_property_variables():
    """Test that all of the observed property variable are returned"""
    catalog = CatalogDjango()
    plugins = [alpha.AlphaSourcePlugin(catalog)]
    catalog.initialize(plugins)
    basin3d_variable = [i.basin3d_id for i in catalog.find_observed_property_variables()]

    print(basin3d_variable)
    assert basin3d_variable == ['PH', 'RDC', 'WLE', 'WT', 'DO', 'SC', 'TDS', 'DIN', 'DTN', 'NH4', 'POC', 'DOC', 'P',
                                'Na', 'K', 'Mg', 'Ca', 'Si', 'Cl', 'SO4', 'NO3', 'NO2', 'S2', 'B', 'Al', 'Sb', 'As',
                                'Ba', 'Be', 'Cd', 'Cr', 'Cu', 'FeT', 'Pb', 'Mo', 'Mn', 'Hg', 'Ni', 'Se', 'Ag', 'Th',
                                'U', 'Zn', 'ACT', 'Ag', 'Al', 'As']


@pytest.mark.django_db
def test_create_catalog():
    """This test creates a catalog"""

    catalog = CatalogDjango()
    plugins = [alpha.AlphaSourcePlugin(catalog)]
    catalog.initialize(plugins)
    expected = ['00400', '00060', '63161', '00010', '00300', '00095', '70301', '00631', '00602', '00608', '00680',
                '00681', '00666', '00930', '00935', '00925', '00915', '01140', '00940', '00945', '00618', '00613',
                '00746', '01020', '01106', '01095', '01000', '01005', '01010', '01025', '01030', '01040', '01046',
                '01049', '01060', '01056', '50287', '01065', '01145', '01075', '01057', '80020', '01090', 'Acetate',
                'Ag', 'Aluminium', 'As']

    datasource_variables = []
    for idx, item in enumerate(catalog.find_observed_properties()):
        datasource_variables.append(item.datasource_variable)
    assert datasource_variables == expected


@pytest.mark.django_db
@pytest.mark.parametrize("plugins, query, expected",
                         [([usgs.USGSDataSourcePlugin],
                           {'variable_name': 'FOO', "datasource_id": 'Alpha'}, None),
                          ([usgs.USGSDataSourcePlugin,
                            alpha.AlphaSourcePlugin],
                           {"datasource_id": 'USGS', 'variable_name': 'Hg'}, {'datasource': {'credentials': {},
                                                                                             'id': 'USGS',
                                                                                             'id_prefix': 'USGS',
                                                                                             'location': 'https://waterservices.usgs.gov/nwis/',
                                                                                             'name': 'USGS'},
                                                                              'datasource_description': 'USGS',
                                                                              'datasource_variable': '50287',
                                                                              'observed_property_variable': {
                                                                                  'basin3d_id': 'Hg',
                                                                                  'categories': ['Biogeochemistry',
                                                                                                 'Trace elements'],
                                                                                  'full_name': 'Mercury (Hg)',
                                                                                  'units': ''},
                                                                              'sampling_medium': 'WATER'}),
                          ([usgs.USGSDataSourcePlugin,
                            alpha.AlphaSourcePlugin],
                           {"datasource_id": 'Alpha', 'variable_name': 'ACT'}, {'datasource': {'credentials': {},
                                                                                               'id': 'Alpha',
                                                                                               'id_prefix': 'A',
                                                                                               'location': 'https://asource.foo/',
                                                                                               'name': 'Alpha'},
                                                                                'datasource_description': 'Alpha',
                                                                                'datasource_variable': 'Acetate',
                                                                                'observed_property_variable': {
                                                                                    'basin3d_id': 'ACT',
                                                                                    'categories': ['Biogeochemistry',
                                                                                                   'Anions'],
                                                                                    'full_name': 'Acetate (CH3COO)',
                                                                                    'units': ''},
                                                                                'sampling_medium': 'WATER'}),
                          ([usgs.USGSDataSourcePlugin,
                            alpha.AlphaSourcePlugin], {"datasource_id": 'FOO', 'variable_name': 'ACT'},
                           None)
                          ],
                         ids=['Wrong-Alpha', 'USGS-plus', 'Alpha-plus', 'Bad-DataSource'])
def test_observed_property(plugins, query, expected):
    """ Test observed property """

    catalog = CatalogDjango()
    catalog.initialize([p(catalog) for p in plugins])

    observed_property = catalog.find_observed_property(**query)
    if expected is None:
        assert observed_property == expected
    else:
        assert observed_property.to_dict() == expected
