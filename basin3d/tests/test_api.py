import json

from basin3d.tests import configure

# Load test settings
configure()

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class TestRegionAPI(TestCase):
    """
    Test /v1/regions api
    """
    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/v1/regions/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [{"id": "A-SI123", "geom": None, "description": "This is for my site description",
                              'name': 'a site',
                           'model_domains': 'http://testserver/v1/regions/A-SI123/model_domains',
                           "url": "http://testserver/v1/regions/A-SI123/"}]

                         )


    def test_get_detail(self):
        response = self.client.get('/v1/regions/A-SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "A-SI123", "geom": None, "description": "This is for my site description",
                          'name': 'a site',
                          'model_domains': 'http://testserver/v1/regions/A-SI123/model_domains',
                          "url": "http://testserver/v1/regions/A-SI123/"})

    def test_get_detail_missing(self):
        response = self.client.get('/v1/regions/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/v1/regions/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                    "'B' is invalid.",
                          'success': False})


class TestModelAPI(TestCase):
    """
    Test /v1/models api
    """
    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/v1/models/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-M0",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "1D",
                                 'web_location': None,
                                 "url": "http://testserver/v1/models/A-M0/"
                             },
                             {
                                 "id": "A-M1",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "2D",
                                 'web_location': None,
                                 "url": "http://testserver/v1/models/A-M1/"
                             },
                             {
                                 "id": "A-M2",
                                 "name": None,
                                 "version": "1.0",
                                 "dimensionality": "3D",
                                 'web_location': None,
                                 "url": "http://testserver/v1/models/A-M2/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/v1/models/A-M2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-M2",
                             "name": None,
                             "version": "1.0",
                             "dimensionality": "3D",
                             'web_location': None,
                             "url": "http://testserver/v1/models/A-M2/"
                         })

    def test_get_detail_missing(self):
        response = self.client.get('/v1/models/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/v1/models/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                    "'B' is invalid.",
                          'success': False})


class TestModelDomainAPI(TestCase):
    """
    Test /v1/model_domains api
    """
    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        response = self.client.get('/v1/model_domains/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         [
                             {
                                 "id": "A-MD1",
                                 "name": "model domain 1",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD1/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD1/"
                             },
                             {
                                 "id": "A-MD2",
                                 "name": "model domain 2",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD2/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD2/"
                             },
                             {
                                 "id": "A-MD3",
                                 "name": "model domain 3",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD3/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD3/"
                             },
                             {
                                 "id": "A-MD4",
                                 "name": "model domain 4",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD4/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD4/"
                             },
                             {
                                 "id": "A-MD5",
                                 "name": "model domain 5",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD5/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD5/"
                             },
                             {
                                 "id": "A-MD6",
                                 "name": "model domain 6",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD6/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD6/"
                             },
                             {
                                 "id": "A-MD7",
                                 "name": "model domain 7",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD7/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD7/"
                             },
                             {
                                 "id": "A-MD8",
                                 "name": "model domain 8",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD8/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD8/"
                             },
                             {
                                 "id": "A-MD9",
                                 "name": "model domain 9",
                                 "meshes": 'http://testserver/v1/model_domains/A-MD9/meshes',
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/A-MD9/"
                             }
                         ]

        )

    def test_get_detail(self):
        response = self.client.get('/v1/model_domains/A-MD7/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-MD7",
                             "name": "model domain 7",
                             "meshes": 'http://testserver/v1/model_domains/A-MD7/meshes',
                             "geom": {},
                             "url": "http://testserver/v1/model_domains/A-MD7/"
                         })

    def test_get_detail_missing(self):
        response = self.client.get('/v1/model_domains/A-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'content': 'There is no detail for A-FOO', 'success': False})

    def test_get_bad_id_prefix(self):
        response = self.client.get('/v1/model_domains/B-FOO/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                    "'B' is invalid.",
                          'success': False})
