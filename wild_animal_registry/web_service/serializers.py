from rest_framework import serializers
from .models import Animal, Sighting, Species


class AnimalSightingSerializer(serializers.ModelSerializer):
    animal = serializers.PrimaryKeyRelatedField(queryset=Animal.objects.all())

    class Meta:
        model = Sighting
        fields = ('id', 'latitude', 'longitude', 'dttm', 'animal',)


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ('id', 'vernacular_name',)


class AnimalSerializer(serializers.ModelSerializer):
    species = serializers.PrimaryKeyRelatedField(queryset=Species.objects.all())

    class Meta:
        model = Animal
        fields = ('id', 'name', 'species',)

