"""
`basin3d.synthesis.models.serializers`
**************************************

.. currentmodule:: basin3d.synthesis.models.serializers

:synopsis: The BASIN-3D Synthesis Model Serializers
:module author: Val Hendrix <vhendrix@lbl.gov>

Serializers that render :mod:`basin.synthesis.models` from Python objects to `JSON` and back again.

* :class:`IdUrlSerializerMixin` - Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
* :class:`RegionSerializer`
* :class:`ModelSerializer`
* :class:`ModelParameterSerializer`
* :class:`ModelParameterSerializer`
* :class:`MeshSerializer`
* :class:`ModelDomainSerializer`

----------------------------------

"""
from basin3d.serializers import MeasurementVariableSerializer
from basin3d.synthesis.models.field import Region
from basin3d.synthesis.models.simulations import ModelDomain
from rest_framework import serializers
from rest_framework.reverse import reverse


class IdUrlSerializerMixin(object):
    """
    Serializer Mixin to support Hypermedia as the Engine of Application State (HATEOAS).
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the serializer superclass
        super(IdUrlSerializerMixin, self).__init__(*args, **kwargs)

        self.fields["url"] = serializers.SerializerMethodField()

    def get_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='{}-detail'.format(obj.__class__.__name__.lower()),
                           kwargs={'pk': obj.id},
                           request=self.context["request"], )


class RegionSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.Region
    """

    id = serializers.CharField()
    name = serializers.CharField()
    geom = serializers.JSONField()
    description = serializers.CharField()
    model_domains = serializers.SerializerMethodField()

    def create(self, validated_data):
        return Region(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance

    def get_model_domains(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            # FIXME: this will break if there are any query parameters
            url = "{}model_domains".format(self.get_url(obj))
            return url


class ModelSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.simulations.Model
    """

    id = serializers.CharField()
    name = serializers.CharField()
    version = serializers.CharField()
    dimensionality = serializers.CharField()
    web_location = serializers.URLField()

    def create(self, validated_data):
        return ModelSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.version = validated_data.get('version', instance.version)
        instance.dimensionality = validated_data.get('dimensionality', instance.dimensionality)
        instance.web_location = validated_data.get('web_location', instance.web_location)
        return instance


class ModelParameterSerializer(serializers.Serializer):
    """
    Serializes a synthesis.model.simulations.ModelParameter

    """

    id = serializers.CharField()
    model_name = serializers.CharField()
    data_source_name = serializers.CharField()
    value = serializers.FloatField()

    def create(self, validated_data):
        return ModelParameterSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.model_name = validated_data.get('model_name', instance.model_name)
        instance.data_source_name = validated_data.get('data_source_name', instance.data_source_name)
        instance.value = validated_data.get('value', instance.value)
        return instance


class MeshSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.model.simulations.Mesh

    """

    id = serializers.CharField()
    parameters = serializers.ListSerializer(child=ModelParameterSerializer())
    initial_conditions = serializers.ListSerializer(child=MeasurementVariableSerializer())
    geom = serializers.JSONField()

    def create(self, validated_data):
        return MeshSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.parameters = validated_data.get('parameters', instance.parameters)
        instance.initial_conditions = validated_data.get('initial_conditions', instance.initial_conditions)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class ModelDomainSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.simulations.ModelDomain

    """

    id = serializers.CharField()
    name = serializers.CharField()
    geom = serializers.JSONField()
    url = serializers.SerializerMethodField()
    meshes = serializers.SerializerMethodField()

    def create(self, validated_data):
        return ModelDomain(**validated_data)

    def update(self, instance, validated_data):
        instance.model_domain_id = validated_data.get('id', instance.model_domain_id)
        instance.model_domain_name = validated_data.get('name', instance.model_domain_name)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance

    def get_meshes(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            # FIXME: this will break if there are any query parameters
            url = "{}meshes".format(self.get_url(obj))
            return url
