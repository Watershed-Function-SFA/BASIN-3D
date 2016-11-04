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
                         [{"id": "SI123", "geom": None, "description": "This is for my site description",
                           "url": "http://testserver/v1/regions/SI123/"}]

                         )

    def test_get_detail(self):
        response = self.client.get('/v1/regions/SI123/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {"id": "SI123", "geom": None, "description": "This is for my site description",
                          "url": "http://testserver/v1/regions/SI123/"})


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
                                 "id": "M0",
                                 "version": "1.0",
                                 "dimensionality": "1D",
                                 "url": "http://testserver/v1/models/M0/"
                             },
                             {
                                 "id": "M1",
                                 "version": "1.0",
                                 "dimensionality": "2D",
                                 "url": "http://testserver/v1/models/M1/"
                             },
                             {
                                 "id": "M2",
                                 "version": "1.0",
                                 "dimensionality": "3D",
                                 "url": "http://testserver/v1/models/M2/"
                             }
                         ]

                         )

    def test_get_detail(self):
        response = self.client.get('/v1/models/M2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "M2",
                             "version": "1.0",
                             "dimensionality": "3D",
                             "url": "http://testserver/v1/models/M2/"
                         })


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
                                 "model_domain_id": "MD1",
                                 "model_domain_name": "model domain 1",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD1/"
                             },
                             {
                                 "model_domain_id": "MD2",
                                 "model_domain_name": "model domain 2",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD2/"
                             },
                             {
                                 "model_domain_id": "MD3",
                                 "model_domain_name": "model domain 3",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD3/"
                             },
                             {
                                 "model_domain_id": "MD4",
                                 "model_domain_name": "model domain 4",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD4/"
                             },
                             {
                                 "model_domain_id": "MD5",
                                 "model_domain_name": "model domain 5",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD5/"
                             },
                             {
                                 "model_domain_id": "MD6",
                                 "model_domain_name": "model domain 6",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD6/"
                             },
                             {
                                 "model_domain_id": "MD7",
                                 "model_domain_name": "model domain 7",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD7/"
                             },
                             {
                                 "model_domain_id": "MD8",
                                 "model_domain_name": "model domain 8",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD8/"
                             },
                             {
                                 "model_domain_id": "MD9",
                                 "model_domain_name": "model domain 9",
                                 "meshes": [
                                     {
                                         "mesh_id": "1",
                                         "parameters": [],
                                         "initial_conditions": []
                                     }
                                 ],
                                 "geom": {},
                                 "url": "http://testserver/v1/model_domains/MD9/"
                             }
                         ]

        )

    def test_get_detail(self):
        response = self.client.get('/v1/model_domains/MD7/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "model_domain_id": "MD7",
                             "model_domain_name": "model domain 7",
                             "meshes": [
                                 {
                                     "mesh_id": "1",
                                     "parameters": [],
                                     "initial_conditions": []
                                 }
                             ],
                             "geom": {},
                             "url": "http://testserver/v1/model_domains/MD7/"
                         })
