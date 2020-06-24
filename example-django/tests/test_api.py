import json


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
                             "datasources": "http://testserver/datasources/",
                             "observedpropertyvariables": "http://testserver/observedpropertyvariables/",
                             "observedproperty": "http://testserver/observedproperty/",
                             "measurementtvptimeseries": "http://testserver/measurement_tvp_timeseries/",
                             "monitoringfeatures": "http://testserver/monitoringfeatures/"
                         })


class TestSiteAPI(TestCase):
    """
    Test /regions api
    """

    def setUp(self):
        self.client = APIClient()

    # # KEEP until replacement test is built
    # def test_get(self):
    #     self.maxDiff = None
    #     response = self.client.get('/sites/', format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(json.loads(response.content.decode('utf-8')),
    #                      [
    #                          {
    #                              "id": "A-1",
    #                              "name": "Foo",
    #                              "description": "Foo Bar Site",
    #                              "type": "site",
    #                              "country": "US",
    #                              "state_province": "California",
    #                              "utc_offset": -6,
    #                              "center_coordinates": {
    #                                  "datum": "WGS84",
    #                                  "type": "geographic",
    #                                  "latitude": 90.0,
    #                                  "longitude": 90.0,
    #                                  "units": "DS"
    #                              },
    #                              "contacts": [
    #                                  {
    #                                      "first_name": "Barry",
    #                                      "last_name": "Allen",
    #                                      "email": "ballen@foo.bar",
    #                                      "institution": "DC Comics",
    #                                      "role": None
    #                                  }
    #                              ],
    #                              "pi": {
    #                                  "first_name": "Jessica",
    #                                  "last_name": "Jones",
    #                                  "email": "jjones@foo.bar",
    #                                  "institution": "DC Comics",
    #                                  "role": None
    #                              },
    #                              "urls": [
    #                                  "http://foo.bar"
    #                              ],
    #                              "url": "http://testserver/sites/A-1/"
    #                          }
    #                      ]
    #
    #                      )
    #
    # def test_get_detail(self):
    #     response = self.client.get('/regions/A-SI123/', format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(json.loads(response.content.decode('utf-8')),
    #                      {"id": "A-SI123", "geom": None,
    #                       "description": "This is for my site description",
    #                       'name': 'a site',
    #                       "url": "http://testserver/regions/A-SI123/"})
    #
    # def test_get_detail_missing(self):
    #     response = self.client.get('/regions/A-FOO/', format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(json.loads(response.content.decode('utf-8')),
    #                      {'content': 'There is no detail for A-FOO', 'success': False})
    #
    # def test_get_bad_id_prefix(self):
    #     response = self.client.get('/regions/B-FOO/', format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(json.loads(response.content.decode('utf-8')),
    #                      {
    #                          'detail': 'There is no detail for datasource object B-FOO. The datasource id '
    #                                    "'B' is invalid.",
    #                          'success': False})


class TestMeasurementTimeseriesTVPObservationAPI(TestCase):
    """
    Test /measurement_tvp_timeseries api
    """

    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        self.maxDiff = None
        response = self.client.get('/measurement_tvp_timeseries/?monitoring_features=A-1&observed_property_variables=ACT&start_date=01/01/2020', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_output = [
            {
                "id": "A-1",
                "unit_of_measurement": "nm",
                'observed_property_variable': 'ACT',
                "feature_of_interest": {
                    "id": "A-1", "name": "Point Location 1",
                    "description": "The point.",
                    "feature_type": "POINT", "shape": "POINT",
                    "coordinates": {
                        "absolute": {
                            "horizontal_position": [{
                                "units": "DD", "latitude": 70.4657, "y": 70.4657, "x": -20.4567,
                                "longitude": -20.4567, "datum": None, "type": "GEOGRAPHIC"
                            }],
                            "vertical_extent": [{
                                "datum": "NAVD88", "value": 1500.0,
                                "distance_units": "feet", "resolution": None, "type": "ALTITUDE"
                            }]
                        },
                        "representative": {
                            "representative_point_type": None, "representative_point": None,
                            "vertical_position": {
                                "datum": "LS", "value": -0.6, "distance_units": "meters",
                                "type": "DEPTH", "resolution": None
                            }
                        }
                    },
                    "description_reference": None,
                    "observed_property_variables": ["ACT", "Ag"],
                    "related_party": [],
                    "url": "http://testserver/monitoringfeatures/points/A-1/",
                    "utc_offset": None,
                    "related_sampling_feature_complex": [{"related_sampling_feature": "A-Region1",
                                                          "related_sampling_feature_type": "REGION",
                                                          "role": "PARENT",
                                                          "url": "http://testserver/monitoringfeatures/regions/A-Region1/"}],
                },
                "feature_of_interest_type": "POINT",
                "utc_offset": -9,
                "result_points": [["2016-02-01T00:00:00", 0.3454],
                                  ["2016-02-02T00:00:00", 0.6908],
                                  ["2016-02-03T00:00:00", 1.0362],
                                  ["2016-02-04T00:00:00", 1.3816],
                                  ["2016-02-05T00:00:00", 1.7269999999999999],
                                  ["2016-02-06T00:00:00", 2.0724],
                                  ["2016-02-07T00:00:00", 2.4177999999999997],
                                  ["2016-02-08T00:00:00", 2.7632],
                                  ["2016-02-09T00:00:00", 3.1086]],
                "result_quality": "CHECKED",
                "statistic": "MEAN",
                "type": "MEASUREMENT_TVP_TIMESERIES",
                "aggregation_duration": "DAY",
                "phenomenon_time": None
            },
            {
                "id": "A-2",
                'observed_property_variable': 'ACT',
                "feature_of_interest": {
                    "id": "A-2", "name": "Point Location 2",
                    "description": "The point.",
                    "feature_type": "POINT", "shape": "POINT",
                    "coordinates": {
                        "absolute": {
                            "horizontal_position": [{
                                "units": "DD", "latitude": 70.4657, "y": 70.4657, "x": -20.4567,
                                "longitude": -20.4567, "datum": None, "type": "GEOGRAPHIC"
                            }],
                            "vertical_extent": [{
                                "datum": "NAVD88", "value": 1500.0,
                                "distance_units": "feet", "resolution": None, "type": "ALTITUDE"
                            }]
                        },
                        "representative": {
                            "representative_point_type": None, "representative_point": None,
                            "vertical_position": {
                                "datum": "LS", "value": -0.7, "distance_units": "meters",
                                "type": "DEPTH", "resolution": None
                            }
                        }
                    },
                    "description_reference": None,
                    "observed_property_variables": ["ACT", "Ag"],
                    "related_party": [],
                    "url": "http://testserver/monitoringfeatures/points/A-2/",
                    "utc_offset": None,
                    "related_sampling_feature_complex": [{"related_sampling_feature": "A-Region1",
                                                          "related_sampling_feature_type": "REGION",
                                                          "role": "PARENT",
                                                          "url": "http://testserver/monitoringfeatures/regions/A-Region1/"}],
                },
                "feature_of_interest_type": "POINT",
                "utc_offset": -10,
                "unit_of_measurement": "nm",
                "result_points": [["2016-02-01T00:00:00", 0.3454],
                                  ["2016-02-02T00:00:00", 0.6908],
                                  ["2016-02-03T00:00:00", 1.0362],
                                  ["2016-02-04T00:00:00", 1.3816],
                                  ["2016-02-05T00:00:00", 1.7269999999999999],
                                  ["2016-02-06T00:00:00", 2.0724],
                                  ["2016-02-07T00:00:00", 2.4177999999999997],
                                  ["2016-02-08T00:00:00", 2.7632],
                                  ["2016-02-09T00:00:00", 3.1086]],
                "result_quality": "CHECKED",
                "statistic": "MEAN",
                "type": "MEASUREMENT_TVP_TIMESERIES",
                "aggregation_duration": "DAY",
                "phenomenon_time": None
            }]
        self.assertEqual(json.loads(response.content.decode('utf-8')), expected_output)
