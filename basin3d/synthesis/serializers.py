from basin3d.serializers import MeasurementVariableSerializer
from basin3d.tests.test_synthesis_models import ModelDomain
from rest_framework import serializers
from rest_framework.reverse import reverse

from basin3d.synthesis.models import Region


class IdUrlSerializerMixin(object):

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
    geom = serializers.JSONField()
    description = serializers.CharField()

    def create(self, validated_data):
        return Region(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class ModelSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.simulations.Model
    """

    id = serializers.CharField()
    version = serializers.CharField()
    dimensionality = serializers.CharField()

    def create(self, validated_data):
        return ModelSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.version = validated_data.get('version', instance.version)
        instance.dimensionality = validated_data.get('dimensionality', instance.dimensionality)
        return instance


class ModelParameterSerializer(IdUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.model.simulations.ModelParameter

    """

    id = serializers.CharField()
    name = serializers.CharField()
    value = serializers.FloatField()

    def create(self, validated_data):
        return ModelParameterSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.value = validated_data.get('value', instance.value)
        return instance


class MeshSerializer(serializers.Serializer):
    """
    Serializes a synthesis.model.simulations.Mesh

    """

    mesh_id = serializers.CharField()
    parameters = serializers.ListSerializer(child=ModelParameterSerializer())
    initial_conditions = serializers.ListSerializer(child=MeasurementVariableSerializer())

    def create(self, validated_data):
        return MeshSerializer(**validated_data)

    def update(self, instance, validated_data):
        instance.mesh_id = validated_data.get('mesh_id', instance.mesh_id)
        instance.parameters = validated_data.get('parameters', instance.parameters)
        instance.initial_conditions = validated_data.get('initial_conditions', instance.initial_conditions)
        return instance


class ModelDomainSerializer(serializers.Serializer):
    """
    Serializes a synthesis.models.simulations.ModelDomain

    """

    model_domain_id = serializers.CharField()
    model_domain_name = serializers.CharField()
    meshes = serializers.ListSerializer(child=MeshSerializer())
    geom = serializers.JSONField()
    url = serializers.SerializerMethodField()

    def create(self, validated_data):
        return ModelDomain(**validated_data)

    def update(self, instance, validated_data):
        instance.model_domain_id = validated_data.get('model_domain_id', instance.model_domain_id)
        instance.model_domain_name = validated_data.get('model_domain_name', instance.model_domain_name)
        instance.geom = validated_data.get('geom', instance.geom)
        instance.meshes = validated_data.get('meshes', instance.meshes)
        return instance

    def get_url(self, obj):
        """
        Get the url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='modeldomain-detail', kwargs={'pk': obj.model_domain_id}, request=self.context["request"], )


