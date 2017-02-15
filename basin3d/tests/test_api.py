import json
from unittest import mock

from basin3d.tests import configure

# Load test settings
from basin3d.viewsets import DirectAPIViewSet

configure()

from django.test import TestCase, override_settings
import rest_framework
from rest_framework import status
from rest_framework.test import APIClient


# def get_direct_api():
#     def get_url(url, params=None, headers=None, verify=False):
#         """
#         Mock direct calls
#         """
#
#         # Return content and status
#         return type('Dummy', (object,), {
#             "content": b'{"message":"This is a direct call to the datasource", "url":"https://asource.foo/'
#                        + str.encode(url) +
#                        b'"}',
#             "status_code": status.HTTP_200_OK})
#     return get_url
#
#
# class DirectAPITest(rest_framework.test.APITestCase):
#
#     def setUp(self):
#         self.view_retrieve = DirectAPIViewSet.as_view({'get':'retrieve'})
#
#     @mock.patch('basin3d.get_url', return_value=get_direct_api())
#     def test_get_detail(self, mock_get_url):
#         factory = rest_framework.test.APIRequestFactory()
#         request = factory.get('direct/A/')
#         response = self.view_retrieve(request, id_prefix="A")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(json.loads(response.content.decode('utf-8')),
#                          {
#                              "message": "This is a direct call to the datasource",
#                              "url": "http://testserver/direct/A/"
#                          })
#
#         mock_get_url.method.assert_called_once()


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
                         {"direct-apis": "http://testserver/direct/",
                          "synthesis-datasources": "http://testserver/synthesis/datasources/",
                          "synthesis-variables": "http://testserver/synthesis/variables/",
                          "synthesis-measurements": "http://testserver/synthesis/measurements/",
                          "synthesis-regions": "http://testserver/synthesis/regions/",
                          "synthesis-models": "http://testserver/synthesis/models/",
                          "synthesis-modeldomains": "http://testserver/synthesis/model_domains/",
                          "synthesis-modelruns": "http://testserver/synthesis/model_runs/",
                          "synthesis-datapointgroups": "http://testserver/synthesis/data_point_groups/",
                          "synthesis-datapoints": "http://testserver/synthesis/data_points/",
                          "synthesis-mesh": "http://testserver/synthesis/meshes/"}

                         )

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
                             "synthesis-models": "http://testserver/synthesis/models/",
                             "synthesis-modeldomains": "http://testserver/synthesis/model_domains/",
                             "synthesis-modelruns": "http://testserver/synthesis/model_runs/",
                             "synthesis-datapointgroups": "http://testserver/synthesis/data_point_groups/",
                             "synthesis-datapoints": "http://testserver/synthesis/data_points/",
                             "synthesis-mesh": "http://testserver/synthesis/meshes/"})


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
                           'model_domains': 'http://testserver/synthesis/regions/A-SI123/model_domains/',
                           "url": "http://testserver/synthesis/regions/A-SI123/"}]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/regions/A-SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "A-SI123", "geom": None,
                          "description": "This is for my site description",
                          'name': 'a site',
                          'model_domains': 'http://testserver/synthesis/regions/A-SI123/model_domains/',
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


class TestModelAPI(TestCase):
    """
    Test /synthesis/models api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/synthesis/models/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-M0",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "1D",
                                 'web_location': None,
                                 "url": "http://testserver/synthesis/models/A-M0/"
                             },
                             {
                                 "id": "A-M1",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "2D",
                                 'web_location': None,
                                 "url": "http://testserver/synthesis/models/A-M1/"
                             },
                             {
                                 "id": "A-M2",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "3D",
                                 'web_location': None,
                                 "url": "http://testserver/synthesis/models/A-M2/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/models/A-M2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-M2",
                             "name": None,
                             "version": "1.0",
                             "dimensionality": "3D",
                             'web_location': None,
                             "url": "http://testserver/synthesis/models/A-M2/"
                         })

    def test_get_detail_missing(self):
        response = self.client.get('/synthesis/models/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/synthesis/models/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                       "'B' is invalid.",
                             'success': False})


class TestModelDomainAPI(TestCase):
    """
    Test /synthesis/model_domains api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/synthesis/model_domains/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-MD1",
                                 "name": "model domain 1",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD1/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD1/"
                             },
                             {
                                 "id": "A-MD2",
                                 "name": "model domain 2",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD2/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD2/"
                             },
                             {
                                 "id": "A-MD3",
                                 "name": "model domain 3",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD3/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD3/"
                             },
                             {
                                 "id": "A-MD4",
                                 "name": "model domain 4",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD4/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD4/"
                             },
                             {
                                 "id": "A-MD5",
                                 "name": "model domain 5",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD5/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD5/"
                             },
                             {
                                 "id": "A-MD6",
                                 "name": "model domain 6",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD6/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD6/"
                             },
                             {
                                 "id": "A-MD7",
                                 "name": "model domain 7",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD7/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD7/"
                             },
                             {
                                 "id": "A-MD8",
                                 "name": "model domain 8",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD8/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD8/"
                             },
                             {
                                 "id": "A-MD9",
                                 "name": "model domain 9",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD9/meshes/',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD9/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/synthesis/model_domains/A-MD7/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-MD7",
                             "name": "model domain 7",
                             "meshes": 'http://testserver/synthesis/model_domains/A-MD7/meshes/',
                             "geom": {},
                             "url": "http://testserver/synthesis/model_domains/A-MD7/"
                         })

    def test_get_detail_missing(self):
        response = self.client.get('/synthesis/model_domains/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/synthesis/model_domains/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                       "'B' is invalid.",
                             'success': False})


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
                             "measurement": "http://testserver/synthesis/measurements/1/",
                             "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                             'geographical_group_type': 'modeldomain',
                             "start_time": "2016-02-01T00:00:00",
                             "end_time": "2016-02-29T00:00:00",
                             "utc_offset": -8,
                             "data_points": "http://testserver/synthesis/data_point_groups/A-2/datapoints/",
                             "url": "http://testserver/synthesis/data_point_groups/A-2/"
                         })

    def test_get(self):
        response = self.client.get('/synthesis/data_point_groups/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [
            {
                "id": "A-1",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-01-01T00:00:00",
                "end_time": "2016-01-31T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-1/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-1/"
            },
            {
                "id": "A-2",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-02-01T00:00:00",
                "end_time": "2016-02-29T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-2/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-2/"
            },
            {
                "id": "A-3",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-03-01T00:00:00",
                "end_time": "2016-03-31T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-3/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-3/"
            },
            {
                "id": "A-4",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-04-01T00:00:00",
                "end_time": "2016-04-30T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-4/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-4/"
            },
            {
                "id": "A-5",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-05-01T00:00:00",
                "end_time": "2016-05-31T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-5/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-5/"
            },
            {
                "id": "A-6",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-06-01T00:00:00",
                "end_time": "2016-06-30T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-6/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-6/"
            },
            {
                "id": "A-7",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-07-01T00:00:00",
                "end_time": "2016-07-31T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-7/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-7/"
            },
            {
                "id": "A-8",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-08-01T00:00:00",
                "end_time": "2016-08-31T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-8/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-8/"
            },
            {
                "id": "A-9",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/model_domains/A-1/",
                'geographical_group_type': 'modeldomain',
                "start_time": "2016-09-01T00:00:00",
                "end_time": "2016-09-30T00:00:00",
                "utc_offset": -8,
                "data_points": "http://testserver/synthesis/data_point_groups/A-9/datapoints/",
                "url": "http://testserver/synthesis/data_point_groups/A-9/"
            }
        ])


class TestDataPointAPI(TestCase):
    """
    Test /synthesis/data_points api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_detail(self):
        response = self.client.get('/synthesis/data_points/A-2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "url": "http://testserver/synthesis/data_points/A-2/",
                             "id": "A-2",
                             "type": "time_series",
                             "measurement": "http://testserver/synthesis/measurements/1/",
                             "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                             'geographical_group_type': 'mesh',
                             "units": "nm",
                             "value": 0.6906906
                         })

    def test_get(self):
        response = self.client.get('/synthesis/data_points/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')), [
            {
                "url": "http://testserver/synthesis/data_points/A-1/",
                "id": "A-1",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 0.3453453
            },
            {
                "url": "http://testserver/synthesis/data_points/A-2/",
                "id": "A-2",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 0.6906906
            },
            {
                "url": "http://testserver/synthesis/data_points/A-3/",
                "id": "A-3",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 1.0360359000000001
            },
            {
                "url": "http://testserver/synthesis/data_points/A-4/",
                "id": "A-4",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 1.3813812
            },
            {
                "url": "http://testserver/synthesis/data_points/A-5/",
                "id": "A-5",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 1.7267265
            },
            {
                "url": "http://testserver/synthesis/data_points/A-6/",
                "id": "A-6",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 2.0720718000000002
            },
            {
                "url": "http://testserver/synthesis/data_points/A-7/",
                "id": "A-7",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 2.4174171
            },
            {
                "url": "http://testserver/synthesis/data_points/A-8/",
                "id": "A-8",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 2.7627624
            },
            {
                "url": "http://testserver/synthesis/data_points/A-9/",
                "id": "A-9",
                "type": "time_series",
                "measurement": "http://testserver/synthesis/measurements/1/",
                "geographical_group": "http://testserver/synthesis/meshes/A-1/",
                'geographical_group_type': 'mesh',
                "units": "nm",
                "value": 3.1081077
            }
        ])
