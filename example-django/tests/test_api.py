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
                             "synthesis-observedpropertyvariables": "http://testserver/synthesis/observedpropertyvariables/",
                             "synthesis-observedproperty": "http://testserver/synthesis/observedproperty/",
                             "synthesis-measurementtvptimeseries": "http://testserver/synthesis/measurement_tvp_timeseries/",
                             "direct-apis": "http://testserver/direct/",
                             "synthesis-monitoringfeatures": "http://testserver/synthesis/monitoringfeatures/"
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
                             "synthesis-observedpropertyvariables": "http://testserver/synthesis/observedpropertyvariables/",
                             "synthesis-observedproperty": "http://testserver/synthesis/observedproperty/",
                             "synthesis-measurementtvptimeseries": "http://testserver/synthesis/measurement_tvp_timeseries/",
                             "synthesis-monitoringfeatures": "http://testserver/synthesis/monitoringfeatures/"
                         })


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

    """
    # KEEP until replacement test is built
    
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
                                         "institution": "DC Comics",
                                         "role": None
                                     }
                                 ],
                                 "pi": {
                                     "first_name": "Jessica",
                                     "last_name": "Jones",
                                     "email": "jjones@foo.bar",
                                     "institution": "DC Comics",
                                     "role": None
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
    """


class TestMeasurementTimeseriesTVPObservationAPI(TestCase):
    """
    Test /synthesis/measurement_tvp_timeseries api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_detail(self):
        response = self.client.get('/synthesis/measurement_tvp_timeseries/A-1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {
                             "id": "A-1",
                             "unit_of_measurement": "nm",
                             "observed_property": "http://testserver/synthesis/observedproperty/1/",
                             "feature_of_interest": "http://testserver/synthesis/monitoringfeatures/points/A-1/",
                             "feature_of_interest_type": "point",
                             "utc_offset": -9,
                             "result_points": [["2016-02-01", 0.3454],
                                               ["2016-02-02", 0.6908],
                                               ["2016-02-03", 1.0362],
                                               ["2016-02-04", 1.3816],
                                               ["2016-02-05", 1.7269999999999999],
                                               ["2016-02-06", 2.0724],
                                               ["2016-02-07", 2.4177999999999997],
                                               ["2016-02-08", 2.7632],
                                               ["2016-02-09", 3.1086]],
                             "result_quality": "checked",
                             "statistic": "mean",
                             "type": "measurement_tvp_timeseries",
                             "aggregation_duration": "daily",
                             "phenomenon_time": None
                         })

    def test_get(self):
        response = self.client.get('/synthesis/measurement_tvp_timeseries/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_output = [
            {
                "id": "A-1",
                "unit_of_measurement": "nm",
                "observed_property": "http://testserver/synthesis/observedproperty/1/",
                "feature_of_interest": "http://testserver/synthesis/monitoringfeatures/points/A-1/",
                "feature_of_interest_type": "point",
                "utc_offset": -9,
                "result_points": [["2016-02-01", 0.3454],
                                  ["2016-02-02", 0.6908],
                                  ["2016-02-03", 1.0362],
                                  ["2016-02-04", 1.3816],
                                  ["2016-02-05", 1.7269999999999999],
                                  ["2016-02-06", 2.0724],
                                  ["2016-02-07", 2.4177999999999997],
                                  ["2016-02-08", 2.7632],
                                  ["2016-02-09", 3.1086]],
                "result_quality": "checked",
                "statistic": "mean",
                "type": "measurement_tvp_timeseries",
                "aggregation_duration": "daily",
                "phenomenon_time": None
            },
            {
                "id": "A-2",
                "observed_property": "http://testserver/synthesis/observedproperty/1/",
                "feature_of_interest_id": "http://testserver/synthesis/monitoringfeatures/points/A-1/",
                "feature_of_interest_type": "point",
                "utc_offset": -10,
                "unit_of_measurement": "nm",
                "result_points": [["2016-02-01", 0.3454],
                                  ["2016-02-02", 0.6908],
                                  ["2016-02-03", 1.0362],
                                  ["2016-02-04", 1.3816],
                                  ["2016-02-05", 1.7269999999999999],
                                  ["2016-02-06", 2.0724],
                                  ["2016-02-07", 2.4177999999999997],
                                  ["2016-02-08", 2.7632],
                                  ["2016-02-09", 3.1086]],
                "result_quality": "checked",
                "statistic": "mean",
                "type": "measurement_tvp_timeseries",
                "aggregation_duration": "daily",
                "phenomenon_time": None
            }]
        self.assertEqual(json.loads(response.content.decode('utf-8')), expected_output)
