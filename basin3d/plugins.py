"""
`basin3d.plugins`
*****************

.. currentmodule:: basin3d.plugins

:platform: Unix, Mac
:synopsis: BASIN-3D ``DataSource`` plugin classes
:module author: Val Hendrix <vhendrix@lbl.gov>

.. contents:: Contents
    :local:
    :backlinks: top

"""
import logging

# Python 3.5 compatibility
import six

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


import yaml
from basin3d import synthesis, get_url, post_url
from basin3d.apps import Basin3DConfig
from basin3d.models import FeatureTypes
from django.apps import apps
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import status


import requests

# Ignore Insecure Warnings in DEBUG Mode
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    if settings.DEBUG:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    pass


__all__ = ['get_url']

logger = logging.getLogger(__name__)


def get_datasource_observed_properties(datasource, variable_names):
    """
    Get the measurement to the specified variable_name

    :param datasource: The DataSource object to act on
    :type datasource: :class: `~basin3d.models.DataSource`
    :param variable_names: the variable names to get the :class:`~basin3d.models.Measurment` for
    :type variable_names: list
    :return: :class:`~basin3d.models.Measurment`
    """
    from basin3d.models import ObservedProperty
    try:
        return ObservedProperty.filter.get(datasource__name=datasource.name,
                                           observed_property_variable_id__in=variable_names)
    except ObservedProperty.DoesNotExist:
        return None


def get_datasource_observed_property(datasource, variable_name):
    """
    Get the measurement to the specified variable_name

    :param datasource: The DataSource object to act on
    :type datasource: :class: `~basin3d.models.DataSource`
    :param variable_name: the variable name to get the :class:`~basin3d.models.Measurment` for
    :return: :class:`~basin3d.models.Measurment`
    """
    from basin3d.models import ObservedProperty
    try:
        return ObservedProperty.objects.get(datasource__name=datasource.name,
                                            observed_property_variable_id=variable_name)
    except ObservedProperty.DoesNotExist:
        return None


def get_datasource_observed_property_variable(datasource, variable_name, from_basin3d=False):
    """
    Convert the given name to either BASIN-3D from :class:`~basin3d.models.DataSource`
    variable name or the other way around.

    :param datasource: The DataSource object to act on
    :type datasource: :class: `~basin3d.models.DataSource`
    :param variable_name:  The :class:`~basin3d.models.MeasurmentVariable`
         name to convert
    :param: from_basin3d: boolean that says whether the variable name is a
        BASIN-3D variable. If not, then this a datasource variable name.
    :type from_basin3d: boolean
    :return: A variable name
    :rtype: str
    """

    from basin3d.models import DataSourceObservedPropertyVariable
    try:
        if from_basin3d:
            # Convert from BASIN-3D to DataSource variable name
            return DataSourceObservedPropertyVariable.objects.get(
                datasource__name=datasource.name,
                observed_property_variable_id=variable_name)
        else:
            # Convert from DataSource variable name to BASIN-3D
            return DataSourceObservedPropertyVariable.objects.get(
                datasource__name=datasource.name,
                name=variable_name)
    except DataSourceObservedPropertyVariable.DoesNotExist:
        return None


def get_datasource_observed_property_variables(datasource, variable_names=None, from_basin3d=False):
    """
    Convert the given list of names to either BASIN-3D from :class:`~basin3d.models.DataSource`
    variable name or the other way around.

    :param datasource: The DataSource object to act on
    :type datasource: :class: `~basin3d.models.DataSource`
    :param variable_names:  The :class:`~basin3d.models.ObservedPropertyVariable`
         names to convert
    :type variable_names: iterable
    :param: from_basin3d: boolean that says whether the variable name is a
        BASIN-3D variable. If not, then this a datasource variable names.
    :type from_basin3d: boolean
    :return: list of variables
    :rtype: iterable
    """
    from basin3d.models import DataSourceObservedPropertyVariable
    if from_basin3d and variable_names:
        # Convert from BASIN-3D to DataSource variable name
        return DataSourceObservedPropertyVariable.objects.filter(
            datasource__name=datasource.name,
            observed_property_variable_id__in=set(variable_names))
    elif variable_names:
        # Convert from DataSource variable name to BASIN-3D
        return DataSourceObservedPropertyVariable.objects.filter(
            datasource__name=datasource.name,
            name__in=set(variable_names))
    else:
        # Return all available variables
        return DataSourceObservedPropertyVariable.objects.filter(
            datasource__name=datasource.name)


def get_request_feature_type(request, return_format="enum"):
    """
    Return the feature type if exists in the request
    :param request: request
    :param return_format: "enum" (default) = the FeatureTypes enum,
                   otherwise return the text version
    :return: the feature_type in the format specified, None if none exists
    """
    path_info = request.path_info.split("/")
    for k, feature_type in FeatureTypes.TYPES.items():
        ft = "{}s".format("".join(feature_type.lower().split()))
        if ft in path_info:
            if return_format == "enum":
                return k
            else:
                return feature_type
    return None


class DataSourcePluginViewMeta(type):
    """
    Metaclass for DataSource plugin views.  The should be registered in a subclass of
    :class:`basin3d.plugins.DataSourcePluginPoint` in attribute `plugin_view_classes`.
    """

    def __new__(cls, name, parents, dct):

        # If there is an init method, we want to modify it
        # to accept a DataSource instance
        old_init=None
        if "__init__" in dct:
            old_init = dct["__init__"]

        def get_observed_properties(self, variable_names):
            """
            Get the measurement to the specified variable_name

            :param variable_names: the variable names to get the :class:`~basin3d.models.ObservedProperty` for
            :type variable_names: list
            :return: :class:`~basin3d.models.ObservedProperty`
            """
            return get_datasource_observed_properties(self.datasource, variable_names)

        def get_observed_property(self, variable_name):
            """
            Get the measurement to the specified variable_name

            :param variable_name: the variable name to get the :class:`~basin3d.models.ObservedProperty` for
            :return: :class:`~basin3d.models.ObservedProperty`
            """
            return get_datasource_observed_property(self.datasource, variable_name)

        def get_observed_property_variable(self, variable_name, from_basin3d=False):
            """
            Convert the given name to either BASIN-3D from :class:`~basin3d.models.DataSource`
            variable name or the other way around.

            :param variable_name:  The :class:`~basin3d.models.ObservedPropertyVariable`
                 name to convert
            :param: from_basin3d: boolean that says whether the variable name is a
                BASIN-3D variable. If not, then this a datasource variable name.
            :type from_basin3d: boolean
            :return: A variable name
            :rtype: str
            """

            return get_datasource_observed_property_variable(self.datasource, variable_name, from_basin3d)

        def get_observed_property_variables(self, variable_names=None, from_basin3d=False):
            """
            Convert the given list of names to either BASIN-3D from :class:`~basin3d.models.DataSource`
            variable name or the other way around.

            :param variable_names:  The :class:`~basin3d.models.ObservedPropertyVariable`
                 names to convert
            :type variable_names: iterable
            :param: from_basin3d: boolean that says whether the variable name is a
                BASIN-3D variable. If not, then this a datasource variable names.
            :type from_basin3d: boolean
            :return: list of variable names
            :rtype: iterable
            """
            return get_datasource_observed_property_variables(self.datasource, variable_names, from_basin3d)

        def new_init(self, *args, **kwargs):

            DataSource = apps.get_app_config(Basin3DConfig.name).get_model('DataSource')

            # if there is an init, execute it
            if old_init:
                old_init(self, *args, **kwargs) # original init

            if not args and len(args) == 0 and not isinstance(args[0],DataSource):
                raise ValueError("Must specify an argument of type {}".format(DataSource))

            self.datasource = args[0]

        # Add methods
        dct["__init__"] = new_init # replace the original init
        dct["get_observed_property_variables"] = get_observed_property_variables  # add get variables
        dct["get_observed_property_variable"] = get_observed_property_variable
        dct["get_observed_property"] = get_observed_property
        dct["get_observed_properties"] = get_observed_properties

        return type.__new__(cls, name, parents, dct)

    def __init__(cls, name, parents, dct):

        if "synthesis_model_class" in dct:
            synthesis_model_class = dct["synthesis_model_class"]
            if isinstance(synthesis_model_class, str):
                class_name_list = synthesis_model_class.split(".")
                module_name = synthesis_model_class.replace(".{}".format(class_name_list[-1]), "")
                module = __import__(module_name)
                synthesis_model_class = getattr(module, class_name_list[-1])

            if not isinstance(synthesis_model_class, synthesis.models.Base):
                ValueError("synthesis_model_class for {} must extend from synthesis.Base".format(
                    DataSourcePluginViewMeta.__name__))

        else:
            raise ValueError("Must define a synthesis_model_class for {}".format(DataSourcePluginViewMeta.__name__))

        # we need to call type.__init__ to complete the initialization
        super(DataSourcePluginViewMeta, cls).__init__(name, parents, dct)


class PluginMount(type):
    """
    The idea for the Simple Plugin Framework comes from a post
    by Marty Alchin on January 10, 2008 about Django

    See: http://martyalchin.com/2008/jan/10/simple-plugin-framework/

    it is under CC-BY-SA 3.0 US License
    (https://creativecommons.org/licenses/by-sa/3.0/us/)

    Plugin classes that extend this will register themselves as
    soon as they are loaded

    """

    def __init__(cls, name, bases, attrs):
        if cls.__name__ == 'DataSourcePluginPoint':
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            PluginMount.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            PluginMount.plugins.append(cls)


class DataSourcePluginPoint(six.with_metaclass(PluginMount, object)):
    """
    Base class for DataSourcePlugins.
    """

    def direct(self, request, direct_path, **kwargs):
        """
        Direct call to api
        :param request:
        :param direct_path:
        :param kwargs:
        :return:
        """

        datasource = self.get_datasource()

        if hasattr(self.get_meta(), "connection_class"):
            http_auth = self.get_meta().connection_class(datasource)

            try:
                if request.method == "GET":
                    response = http_auth.get("{}{}".format(datasource.location, direct_path),
                                         params=request.query_params)
                elif request.method == "POST":
                    response = http_auth.post("{}{}".format(datasource.location, direct_path),
                                              params=request.data)

            finally:
                http_auth.logout()
        else:
            try:
                if request.method == "GET":
                    response = get_url("{}{}".format(datasource.location, direct_path))
                elif request.method == "POST":
                    response = post_url("{}{}".format(datasource.location, direct_path),
                                              params=request.data)
            except Exception as e:
                response = JsonResponse(data={"error": str(e)},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not response:
            try:
                response = JsonResponse(data={"error": response.json()},
                                        status=response.status_code)
            except JSONDecodeError:
                response = HttpResponse(response.content,
                                        status=response.status_code)
        else:
            try:
                if hasattr(response, "json"):
                    response.json()
            except JSONDecodeError:
                response = JsonResponse(data={"error": "Did not receive a JSON Response"},
                                        status=response.status_code)

        return response

    @classmethod
    def get_meta(cls):
        """
        Gets the DataSourceMeta internal class that should be defined by subclasses.
        Raises an error if it is not found
        :return:
        """
        meta = getattr(cls, 'DataSourceMeta', None)

        if not meta:
            raise ValueError("Must define inner class DatasSourceMeta for {}".format(cls))
        return meta

    @classmethod
    def get_datasource(cls):
        """
        Get the `basin3d.models.DataSource` record for the subclass of this Plugin.
        :return:
        """
        meta = cls.get_meta()
        datasource_id = getattr(meta, 'id', None)
        if datasource_id:
            DataSource = apps.get_app_config(Basin3DConfig.name).get_model('DataSource')
            obj = DataSource.objects.get(name=datasource_id)
            return obj
        else:
            raise ValueError("{}.DataSourceMeta does not define an 'id'.")

    @classmethod
    def get_plugin_views(cls):
        """
        Get the defined plugin_view_classes from the subclass.  These should be defined in
        `DataSourceMeta.plugin_view_subclass`. If not, an error is thrown
        :return:
        """
        view_classes = {}
        plugin_view_classes = getattr(cls, 'plugin_view_classes', None)
        if plugin_view_classes:
            for view_class in plugin_view_classes:
                view = view_class(cls.get_datasource())
                view_classes[view.synthesis_model_class] = view

        return view_classes

    @classmethod
    def get_id_prefix(cls):
        """
        Get the defined id prefix
        """
        meta = cls.get_meta()
        id_prefix = getattr(meta, 'id_prefix', None)
        if not id_prefix:
            raise ValueError("{}.DataSourceMeta does not define an 'id_prefix'.")

    @classmethod
    def get_feature_types(cls):
        """
        Get the defined feature types
        :return:
        """
        return getattr(cls, 'feature_types', None)


class HTTPConnectionDataSource(object):
    """
    Class for handling Authentication and authorization of
    :class:`basin3d.models.DataSource` over HTTP


    :param datasource: the datasource to authenticate and authorize via HTTP
    :type datasource: :class:`basin3d.models.DataSource` instance
    """

    def __init__(self, datasource, *args, **kwargs):
        self.datasource = datasource
        self.credentials = None
        self.verify_ssl = True
        if datasource.get_plugin().DataSourceMeta.id in settings.BASIN3D and \
                        'VERIFY_SSL' in settings.BASIN3D[
                    datasource.get_plugin().DataSourceMeta.id]:
            self.verify_ssl = settings.BASIN3D[datasource.get_plugin().DataSourceMeta.id][
                'VERIFY_SSL']

    def login(self):
        """
        Login to the :class:`basin3d.models.DataSource`

        :return: JSON response
        :rtype: dict
        """
        raise NotImplemented

    def logout(self):
        """
        Login out of the :class:`basin3d.models.DataSource`

        :return: None
        """
        raise NotImplemented

    def get(self, url_part, params=None, headers=None):
        """
        The resources at the spedicfied url

        :param url_part:
        :param params:
        :param headers:
        :return:
        """
        raise NotImplemented

    def post(self, url_part, params=None, headers=None):
        """
        The resources at the spedicfied url

        :param url_part:
        :param params:
        :param headers:
        :return:
        """
        raise NotImplemented

    @classmethod
    def get_credentials_format(cls):
        """
        This returnes the format that the credentials are stored in the DB
        :return: The format for the credentials
        """
        raise NotImplemented


class InvalidOrMissingCredentials(Exception):
    """The credentials are invalid or missing"""
    pass


class HTTPOAuth2DataSource(HTTPConnectionDataSource):
    """
    Class for handling Authentication and authorization of
    :class:`basin3d.models.DataSource` over HTTP with OAuth2


    :param datasource: the datasource to authenticate and authorize via HTTP
    :type datasource: :class:`basin3d.models.DataSource` instance
    :param auth_token_path: The url part for requesting a token
    :param revoke_token_path: The url part for revoking a valid token
    :param auth_scope: The scope of the token being requested (e.g read, write, group)
    :param grant_type: The type of oauth2 grant (e.g client_credentials, password,
            refresh_token, authorization_code)

    """

    CREDENTIALS_FORMAT = 'client_id:\nclient_secret:\n'

    def __init__(self, datasource, *args, auth_token_path="o/token/",
                 revoke_token_path="o/revoke_token/", auth_scope="read",
                 grant_type="client_credentials",
                 **kwargs):

        super(HTTPOAuth2DataSource, self).__init__(datasource, *args, **kwargs)
        self.token = None
        self.auth_token_path = auth_token_path
        self.revoke_token_path = revoke_token_path
        self.auth_scope = auth_scope
        self.grant_type = grant_type
        self.client_id, self.client_secret = self._load_credentials(datasource)

    def _validate_credentials(self):
        """
        Validate the Data Source credentials

        :return: TRUE if the credentials are valid
        :rtype: boolean
        """

        # There should be a client_id and client secret
        return "client_id" in self.credentials.keys() and "client_secret" in self.credentials.keys() \
               and self.credentials["client_id"] and self.credentials["client_secret"]

    def _load_credentials(self, datasource):
        """
        Get the credentials from Data Source. If the
        credentials are invalid `None` is returned.

        :param datasource: The datasource object
        :type datasource: :class:`basin3d.models.DataSource`
        :return: tuple of client_id and client_secret
        :rtype: tuple
        """

        self.credentials = datasource.credentials  # Access the credentials

        # If there are credentials then make the api call
        if self.credentials:
            self.credentials = yaml.load(self.credentials)
            if self._validate_credentials():
                return self.credentials["client_id"], self.credentials["client_secret"]
            raise InvalidOrMissingCredentials("client_id and client_secret are missing or invalid")

        return None,None

    @staticmethod
    def get_credentials_format():
        """
        :return: The format for the credentials
        """
        return HTTPOAuth2DataSource.CREDENTIALS_FORMAT

    def login(self):
        """
        Get a token

        OAuth Client credentials (client_id, client_secret) stored in the
        DataSource.

            - *Url:* https://:class:`basin3d.models.DataSource.location`<auth_token_path>
            - *Scope:* <token_scope>
            - *Grant Type:* <grant_type>
            - *Client Id:* stored in encrypted :class:`basin3d.models.DataSource` field
            - *Client Secret:* stored in encrypted :class:`basin3d.models.DataSource` field


        Example JSON Response::

            {
                "access_token": "<your_access_token>",
                "token_type": "Bearer",
                "expires_in": 36000,
                "refresh_token": "<your_refresh_token>",
                "scope": "read"
            }


        """

        # Build the authentication url
        url = '{}{}'.format(self.datasource.location,self.auth_token_path)
        try:

            # Login to the Data Source
            res = requests.post(url, params={"scope": self.auth_scope, "grant_type": self.grant_type},
                                auth=(self.client_id, self.client_secret),
                                verify=self.verify_ssl)

            # Validate the response
            if res.status_code != requests.codes.ok:
                logger.error("Authentication  error {}: {}".format(url, res.content))
                return None

            # Get the JSON content (This has the token)
            result_json = res.json()
            self.token = result_json
        except Exception as e:
            logger.error("Authentication  error {}: {}".format(url, e))
            # Access is denied!!
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()

    def get(self, url_part, params=None, headers=None):
        """
        Login Data Source if not already logged in.
        Access url with the Authorization header and the access token

        Authorization Header:
            - Authorization": "{token_type} {access_token}

        :param url_part: The url part to request
        :param params: additional parameters for the request
        :type params: dict
        :param headers: request headers
        :return: None
        :raises: PermissionDenied
        """
        if not self.token:
            self.login()
        if not self.token:
            # Access is denied!!
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()

        # Prepare the Authorization header
        auth_headers = {"Authorization": "{token_type} {access_token}".format(**self.token)}
        if headers:
            auth_headers.update(headers)

        return get_url(url_part, params=params, headers=auth_headers, verify=self.verify_ssl)

    def post(self, url_part, params=None, headers=None):
        """
        Login Data Source if not already logged in.
        Access url with the Authorization header and the access token

        Authorization Header:
            - Authorization": "{token_type} {access_token}

        :param url_part: The url part to request
        :param params: additional parameters for the request
        :type params: dict
        :param headers: request headers
        :return: None
        :raises: PermissionDenied
        """

        if not self.token:
            self.login()
        if not self.token:
            # Access is denied!!
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied()

        # Prepare the Authorization header
        auth_headers = {"Authorization": "{token_type} {access_token}".format(**self.token)}
        if headers:
            auth_headers.update(headers)

        return post_url(url_part, params=params, headers=auth_headers, verify=self.verify_ssl)

    def logout(self):
        """
        Revokes atoken

        :param token: The current Token
        :return: None
        """

        # Build the authentication url for revoking the token
        url = '{}{}'.format(self.datasource.location,self.revoke_token_path)

        # Request the token to be revoked
        if self.token:
            res = requests.post(url, params={"token": self.token["access_token"],
                                         "client_id": self.client_id},
                            auth=(self.client_id, self.client_secret),
                            verify=self.verify_ssl)

            # Validate the success of the token revocation
            from rest_framework import status
            if res.status_code != status.HTTP_200_OK:
                logger.warn("Problem encountered revoking token for '{}' HTTP status {} -- {}".format(
                    self.datasource.name,
                    res.status_code, res.content.decode('utf-8')))
