from rest_framework import serializers

from iris.models import PersonIrisCompare


class PersonIrisCompareSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonIrisCompare
        fields = ('percentage',)