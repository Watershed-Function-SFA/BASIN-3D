from rest_framework import serializers
from rest_framework.reverse import reverse

from basin3d.synthesis.models import Site, Location, DataPoint


class SiteUrlSerializerMixin(object):
    """
    SerilizerMixin that add a Site Url to a serizliaer

    """
    site = serializers.SerializerMethodField(method_name='site_url')  # see get_site()

    def __init__(self, *args, **kwargs):
        # Instantiate the serializer superclass
        super(SiteUrlSerializerMixin, self).__init__(*args, **kwargs)

        self.fields["site"] = SiteUrlSerializerMixin.site

    def site_url(self, obj):
        """
        Get the Site url based on the current context
        :param obj:
        :return:
        """
        if "request" in self.context and self.context["request"]:
            return reverse(viewname='site-detail', kwargs={'pk': obj.site_id}, request=self.context["request"], )


class SiteSerializer(SiteUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.Site
    """

    site_id = serializers.CharField()
    country = serializers.CharField(max_length=50)
    contact_name = serializers.CharField()
    contact_email = serializers.EmailField()
    contact_institution = serializers.CharField()
    urls = serializers.ListSerializer(child=serializers.URLField())
    geom = serializers.JSONField()

    def create(self, validated_data):
        return Site(**validated_data)

    def update(self, instance, validated_data):
        instance.site_id = validated_data.get('site_id', instance.site_id)
        instance.country = validated_data.get('country', instance.country)
        instance.contact_name = validated_data.get('contact_name', instance.contact_name)
        instance.contact_email = validated_data.get('contact_email', instance.contact_email)
        instance.contact_institution = validated_data.get('contact_institution', instance.contact_institution)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class LocationSerializer(SiteUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.Location
    """

    site_id = serializers.CharField()
    location_id = serializers.CharField()
    name = serializers.CharField()
    group = serializers.CharField()
    type = serializers.CharField()
    geom = serializers.JSONField()
    measure_variables = serializers.ListField()

    def create(self, validated_data):
        return Location(**validated_data)

    def update(self, instance, validated_data):
        instance.site_id = validated_data.get('site_id', instance.site_id)
        instance.location_id = validated_data.get('location_id', instance.location_id)
        instance.name = validated_data.get('name', instance.name)
        instance.group = validated_data.get('group', instance.group)
        instance.type = validated_data.get('type', instance.type)
        instance.geom = validated_data.get('geom', instance.geom)
        return instance


class DataPointSerializer(SiteUrlSerializerMixin, serializers.Serializer):
    """
    Serializes a synthesis.models.Location
    """

    type = serializers.CharField()
    location_id = serializers.CharField()
    depth = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    value = serializers.FloatField()
    unit = serializers.CharField()
    average = serializers.CharField()

    def create(self, validated_data):
        return DataPoint(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.location_id = validated_data.get('location_id', instance.location_ud)
        instance.depth = validated_data.get('depth', instance.depth)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.value = validated_data.get('value', instance.value)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.average = validated_data.get('average', instance.average)
        return instance
