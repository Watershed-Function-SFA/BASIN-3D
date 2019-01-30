import json

import rest_framework
from basin3d.viewsets import DirectAPIViewSet

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from unittest import mock


def get_direct_api():
    # Return content and status
    return type('Response', (object,), {
        "json": lambda: json.loads("kdshfjsdohf"),
        "status_code": status.HTTP_200_OK})


class DirectAPITest(rest_framework.test.APITestCase):
    def setUp(self):
        self.view_retrieve = DirectAPIViewSet.as_view({'get': 'retrieve'})
        self.view_post_retrieve = DirectAPIViewSet.as_view({'post': 'retrieve'})

    @mock.patch('basin3d.plugins.get_url')
    def test_get_detail(self, mock_get_url):
        mock_get_url.return_value = get_direct_api()
        import basin3d
        basin3d.get_url = mock_get_url
        factory = rest_framework.test.APIRequestFactory()
        request = factory.get('direct/A/')
        response = self.view_retrieve(request, id_prefix="A")
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'error': 'Did not receive a JSON Response'})

    @mock.patch('basin3d.plugins.post_url')
    def test_post_detail(self, mock_post_url):
        mock_post_url.return_value = get_direct_api()
        import basin3d
        basin3d.post_url = mock_post_url
        factory = rest_framework.test.APIRequestFactory()
        request = factory.post('direct/A/')
        response = self.view_post_retrieve(request, id_prefix="A")
        response.render()
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'error': 'Did not receive a JSON Response'})


class TestAPIRoot(TestCase):
    """
    Test the broker root API
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "synthesis-datasources": "http://testserver/synthesis/datasources/",
                             "synthesis-variables": "http://testserver/synthesis/variables/",
                             "synthesis-measurements": "http://testserver/synthesis/measurements/",
                             "synthesis-regions": "http://testserver/synthesis/regions/",
                             "synthesis-sites": "http://testserver/synthesis/sites/",
                             "synthesis-plots": "http://testserver/synthesis/plots/",
                             "synthesis-pointlocations": "http://testserver/synthesis/point_locations/",
                             "synthesis-datapointgroups": "http://testserver/synthesis/data_point_groups/",
                             "synthesis-datapoints": "http://testserver/synthesis/data_points/",
                             "direct-apis": "http://testserver/direct/"
                         })

    @override_settings(BASIN3D={'SYNTHESIS': False, 'DIRECT_API': True})
    def test_get_direct_api_only(self):
        response = self.client.get('/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"direct-apis": "http://testserver/direct/"})

    @override_settings(BASIN3D={'SYNTHESIS': True, 'DIRECT_API': False})
    def test_get_synthesis_only(self):
        response = self.client.get('/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "synthesis-datasources": "http://testserver/synthesis/datasources/",
                             "synthesis-variables": "http://testserver/synthesis/variables/",
                             "synthesis-measurements": "http://testserver/synthesis/measurements/",
                             "synthesis-regions": "http://testserver/synthesis/regions/",
                             "synthesis-sites": "http://testserver/synthesis/sites/",
                             "synthesis-plots": "http://testserver/synthesis/plots/",
                             "synthesis-pointlocations": "http://testserver/synthesis/point_locations/",
                             "synthesis-datapointgroups": "http://testserver/synthesis/data_point_groups/",
                             "synthesis-datapoints": "http://testserver/synthesis/data_points/"})


class TestDirectAPIRoot(TestCase):
    """
    Test the direct API
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/direct/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "Alpha": "http://testserver/direct/A/"
                             }
                         ]

                         )


class TestSiteAPI(TestCase):
    """
    Test /synthesis/regions api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        self.maxDiff = None
        response = self.client.get('/synthesis/sites/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-1",
                                 "name": "Foo",
                                 "description": "Foo Bar Site",
                                 "type": "site",
                                 "country": "US",
                                 "state_province": "California",
                                 "utc_offset": -6,
                                 "center_coordinates": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DS"
                                 },
                                 "contacts": [
                                     {
                                         "first_name": "Barry",
                                         "last_name": "Allen",
                                         "email": "ballen@foo.bar",
                                         "institution": "DC Comics"
                                     }
                                 ],
                                 "pi": {
                                     "first_name": "Jessica",
                                     "last_name": "Jones",
                                     "email": "jjones@foo.bar",
                                     "institution": "DC Comics"
                                 },
                                 "urls": [
                                     "http://foo.bar"
                                 ],
                                 "url": "http://testserver/synthesis/sites/A-1/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/regions/A-SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "A-SI123", "geom": None,
                          "description": "This is for my site description",
                          'name': 'a site',
                          "url": "http://testserver/synthesis/regions/A-SI123/"})

    def test_get_detail_missing(self):
        response = self.client.get('/synthesis/regions/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/synthesis/regions/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                       "'B' is invalid.",
                             'success': False})


class TestRegionAPI(TestCase):
    """
    Test /synthesis/regions api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/synthesis/regions/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [{"id": "A-SI123", "geom": None,
                           "description": "This is for my site description",
                           'name': 'a site',
                           "url": "http://testserver/synthesis/regions/A-SI123/"}]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/regions/A-SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "A-SI123", "geom": None,
                          "description": "This is for my site description",
                          'name': 'a site',
                          "url": "http://testserver/synthesis/regions/A-SI123/"})

    def test_get_detail_missing(self):
        response = self.client.get('/synthesis/regions/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/synthesis/regions/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                       "'B' is invalid.",
                             'success': False})


class TestPointLocationAPI(TestCase):
    """
    Test /synthesis/point_locations api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/synthesis/point_locations/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-0",
                                 "name": "Point Location 0",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-0/"
                             },
                             {
                                 "id": "A-1",
                                 "name": "Point Location 1",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-1/"
                             },
                             {
                                 "id": "A-2",
                                 "name": "Point Location 2",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-2/"
                             },
                             {
                                 "id": "A-3",
                                 "name": "Point Location 3",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-3/"
                             },
                             {
                                 "id": "A-4",
                                 "name": "Point Location 4",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-4/"
                             },
                             {
                                 "id": "A-5",
                                 "name": "Point Location 5",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-5/"
                             },
                             {
                                 "id": "A-6",
                                 "name": "Point Location 6",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-6/"
                             },
                             {
                                 "id": "A-7",
                                 "name": "Point Location 7",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-7/"
                             },
                             {
                                 "id": "A-8",
                                 "name": "Point Location 8",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-8/"
                             },
                             {
                                 "id": "A-9",
                                 "name": "Point Location 9",
                                 "description": None,
                                 "type": "pointlocation",
                                 "site": "http://testserver/synthesis/sites/A-1/",
                                 "geographical_group": "http://testserver/synthesis/plots/A-1/",
                                 "geographical_group_type": "plot",
                                 "horizontal_position": {
                                     "datum": "WGS84",
                                     "type": "geographic",
                                     "latitude": 90.0,
                                     "longitude": 90.0,
                                     "units": "DD"
                                 },
                                 "vertical_extent": None,
                                 "measure_variables": None,
                                 "url": "http://testserver/synthesis/point_locations/A-9/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/point_locations/A-0/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-0",
                             "name": "Point Location 0",
                             "description": None,
                             "type": "pointlocation",
                             "site": "http://testserver/synthesis/sites/A-1/",
                             "geographical_group": "http://testserver/synthesis/plots/A-1/",
                             "geographical_group_type": "plot",
                             "horizontal_position": {
                                 "datum": "WGS84",
                                 "type": "geographic",
                                 "latitude": 90.0,
                                 "longitude": 90.0,
                                 "units": "DD"
                             },
                             "vertical_extent": None,
                             "measure_variables": None,
                             "url": "http://testserver/synthesis/point_locations/A-0/"
                         })


class TestDataPointGroupAPI(TestCase):
    """
    Test /synthesis/data_point_groups api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_detail(self):
        response = self.client.get('/synthesis/data_point_groups/A-2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-2",
                             "units": None,
                             "measurement": "http://testserver/synthesis/measurements/1/",
                             "geographical_group": "http://testserver/synthesis/sites/A-1/",
                             "geographical_group_type": "site",
                             "utc_offset": -8,
                             "data_points": "http://testserver/synthesis/data_point_groups/A-2/datapoints/"
                         })

    def test_get(self):
        response = self.client.get('/synthesis/data_point_groups/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [
            {
                "id": "A-1",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-1/datapoints/"
            },
            {
                "id": "A-2",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-2/datapoints/"
            },
            {
                "id": "A-3",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-3/datapoints/"
            },
            {
                "id": "A-4",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-4/datapoints/"
            },
            {
                "id": "A-5",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-5/datapoints/"
            },
            {
                "id": "A-6",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-6/datapoints/"
            },
            {
                "id": "A-7",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-7/datapoints/"
            },
            {
                "id": "A-8",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-8/datapoints/"
            },
            {
                "id": "A-9",
                "units": None,
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/sites/A-1/",
                "geographical_group_type": "site",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-9/datapoints/"
            }
        ])


class TestDataPointAPI(TestCase):
    """
    Test /synthesis/data_points api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_detail(self):
        self.maxDiff = None
        response = self.client.get('/synthesis/data_points/A-2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "url": "http://testserver/synthesis/data_points/A-2/",
                             "id": "A-2",
                             "type": "time_series",
                             "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                             "geographical_group_type": "pointlocation",
                             "units": "nm",
                             "measurement_position": {
                                 "type": "measurementposition",
                                 "point_location": "http://testserver/synthesis/point_locations/A-1/",
                                 "vertical_position": {
                                     "value": 0.7069,
                                     "resolution": None,
                                     "distance_units": "meters",
                                     "datum": "LS",
                                     "type": "depth"
                                 }
                             },
                             "measurement": {
                                 "url": "http://testserver/synthesis/measurements/1/",
                                 "sampling_medium": "water",
                                 "datasource": "Alpha",
                                 "variable": "ACT",
                                 "description": ""
                             },
                             "timestamp": "2016-02-01",
                             "value": 0.6906906,
                             "temporal_resolution": "month",
                             "quality_checked": None,
                             "reference": None,
                             "utc_offset": -8
                         }
                         )

    def test_get(self):
        response = self.client.get('/synthesis/data_points/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [
            {
                "url": "http://testserver/synthesis/data_points/A-1/",
                "id": "A-1",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 0.35345,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-01-01",
                "value": 0.3453453,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-2/",
                "id": "A-2",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 0.7069,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-02-01",
                "value": 0.6906906,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-3/",
                "id": "A-3",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 1.06035,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-03-01",
                "value": 1.0360359000000001,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-4/",
                "id": "A-4",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 1.4138,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-04-01",
                "value": 1.3813812,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-5/",
                "id": "A-5",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 1.76725,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-05-01",
                "value": 1.7267265,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-6/",
                "id": "A-6",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 2.1207,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-06-01",
                "value": 2.0720718000000002,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-7/",
                "id": "A-7",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 2.47415,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-07-01",
                "value": 2.4174171,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-8/",
                "id": "A-8",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 2.8276,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-08-01",
                "value": 2.7627624,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            },
            {
                "url": "http://testserver/synthesis/data_points/A-9/",
                "id": "A-9",
                "type": "time_series",
                "geographical_group": "http://testserver/synthesis/point_locations/A-1/",
                "geographical_group_type": "pointlocation",
                "units": "nm",
                "measurement_position": {
                    "type": "measurementposition",
                    "point_location": "http://testserver/synthesis/point_locations/A-1/",
                    "vertical_position": {
                        "value": 3.18105,
                        "resolution": None,
                        "distance_units": "meters",
                        "datum": "LS",
                        "type": "depth"
                    }
                },
                "measurement": {
                    "url": "http://testserver/synthesis/measurements/1/",
                    "sampling_medium": "water",
                    "datasource": "Alpha",
                    "variable": "ACT",
                    "description": ""
                },
                "timestamp": "2016-09-01",
                "value": 3.1081077,
                "temporal_resolution": "month",
                "quality_checked": None,
                "reference": None,
                "utc_offset": -8
            }
        ])
