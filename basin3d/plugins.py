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
from basin3d import synthesis
from basin3d.apps import Basin3DConfig
from django.apps import apps
from djangoplugins.point import PluginPoint
import requests
import yaml
import logging

__all__ = ['get_url']

logger = logging.getLogger(__name__)


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

        def new_init(self, *args, **kwargs):

            DataSource = apps.get_app_config(Basin3DConfig.name).get_model('DataSource')

            # if there is an init, execute it
            if old_init:
                old_init(self, *args, **kwargs) # original init

            if not args and len(args) == 0 and not isinstance(args[0],DataSource):
                raise ValueError("Must specify an argument of type {}".format(DataSource))

            self.datasource = args[0]

        dct["__init__"] = new_init # replace the original init

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


class DataSourcePluginPoint(PluginPoint):
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
        direct_api = hasattr(self, 'direct_api')

        from rest_framework import status
        from rest_framework.response import Response
        response = Response(status=status.HTTP_404_NOT_FOUND)

        if direct_api:
            response = self.direct_api(datasource, request, direct_path, **kwargs)
            if response:
                return response
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



class HTTPOAuth2DataSource(object):
    """
    Class for handling Authentication and authorization of
    :class:`basin3d.models.DataSource` over HTTP with OAuth2


    :param datasource: the datasource to authenticate and authorize via HTTP
    :type datasource: :class:`basin3d.models.DataSource` instance
    :param verify_ssl: Verify SSL
    :type verify_ssl: boolean

    """

    FORMAT_YAML = 'client_id:\nclient_secret:\n'

    def __init__(self,datasource, verify_ssl=True, auth_token_path="o/token/",
                 revoke_token_path="o/revoke_token/", auth_scope="read",
                 grant_type="client_credential",
                 *args, **kwargs):

        self.datasource = datasource
        self.credentials = None
        self.verify_ssl = verify_ssl
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
        Get the credentials from JAEA Geo Data Source. If the
        credentials are invalid `None` is returned.

        :param datasource: The datasource object
        :type datasource: :class:`basin3d.models.DataSource`
        :return: tuple of client_id and client_secret
        :rtype: tuple
        """

        self.credentials = datasource.credentials  # Access the credentials

        # If there are credentials then get the locations
        if self.credentials:
            c = yaml.load(self.credentials)
            if self._validate_credentials(c):
                return c["client_id"], c["client_secret"]

        return None

    def get_token(self):
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


        :return: JSON response
        :rtype: dict
        """

        # Build the authentication url
        url = '{}{}'.format(self.datasource.location,self.auth_token_path)
        try:

            # Login to the JAEA Geo Data Source
            res = requests.post(url, params={"scope": self.auth_scope, "grant_type": self.grant_type},
                                auth=(self.client_id, self.client_secret),
                                verify=self.verify_ssl)

            # Validate the response
            if res.status_code != requests.codes.ok:
                logger.error("Authentication  error {}: {}".format(url, res.content))
                return None

            # Get the JSON content (This has the token)
            result_json = res.json()
            return result_json
        except Exception as e:
            logger.error("Authentication  error {}: {}".format(url, e))
            return None

    def revoke_token(self, token):
        """
        Revokes atoken

        :param token: The current Token
        :return: None
        """

        # Build the authentication url for revoking the token
        url = '{}{}'.format(self.datasource.location,self.revoke_token_path)

        # Request the token to be revoked
        res = requests.post(url, params={"token": token},
                            auth=(self.client_id, self.client_secret),
                            verify=self.verify_ssl)

        # Validate the success of the token revocation
        from rest_framework import status
        if res.status_code != status.HTTP_200_OK:
            logger.warn("Problem encountered revoking token for '{}' HTTP status {}",
                        self.datasource.name,
                        res.status_code)