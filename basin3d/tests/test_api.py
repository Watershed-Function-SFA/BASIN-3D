import json

from basin3d.tests import configure

# Load test settings
configure()

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


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
                             "direct-apis": "http://testserver/direct/",
                             "synthesis-regions": "http://testserver/synthesis/regions/",
                             "synthesis-models": "http://testserver/synthesis/models/",
                             "synthesis-modeldomains": "http://testserver/synthesis/model_domains/",
                             "synthesis-mesh": "http://testserver/synthesis/meshes/"
                         }

                         )


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

    def test_get_detail(self):
        response = self.client.get('/direct/A/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "message": "This is a direct call to the datasource",
                             "url": "http://testserver/direct/A/"
                         })


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
                         [{"id": "A-SI123", "geom": None, "description": "This is for my site description",
                              'name': 'a site',
                           'model_domains': 'http://testserver/synthesis/regions/A-SI123/model_domains',
                           "url": "http://testserver/synthesis/regions/A-SI123/"}]

                         )


    def test_get_detail(self):
        response = self.client.get('/synthesis/regions/A-SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "A-SI123", "geom": None, "description": "This is for my site description",
                          'name': 'a site',
                          'model_domains': 'http://testserver/synthesis/regions/A-SI123/model_domains',
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
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
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
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
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
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD1/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD1/"
                             },
                             {
                                 "id": "A-MD2",
                                 "name": "model domain 2",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD2/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD2/"
                             },
                             {
                                 "id": "A-MD3",
                                 "name": "model domain 3",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD3/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD3/"
                             },
                             {
                                 "id": "A-MD4",
                                 "name": "model domain 4",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD4/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD4/"
                             },
                             {
                                 "id": "A-MD5",
                                 "name": "model domain 5",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD5/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD5/"
                             },
                             {
                                 "id": "A-MD6",
                                 "name": "model domain 6",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD6/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD6/"
                             },
                             {
                                 "id": "A-MD7",
                                 "name": "model domain 7",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD7/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD7/"
                             },
                             {
                                 "id": "A-MD8",
                                 "name": "model domain 8",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD8/meshes',
                                 "geom": {},
                                 "url": "http://testserver/synthesis/model_domains/A-MD8/"
                             },
                             {
                                 "id": "A-MD9",
                                 "name": "model domain 9",
                                 "meshes": 'http://testserver/synthesis/model_domains/A-MD9/meshes',
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
                             "meshes": 'http://testserver/synthesis/model_domains/A-MD7/meshes',
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
                         {'detail': 'There is no detail for datasource object B-FOO. The datasource id '
                                    "'B' is invalid.",
                          'success': False})
