from rest_framework import serializers
from .models import Animal, Sighting, Species


class AnimalSightingSerializer(serializers.ModelSerializer):
    animal_id = serializers.PrimaryKeyRelatedField(queryset=Animal.objects.all(), source='animal', write_only=True)

    class Meta:
        model = Sighting
        fields = ('id', 'latitude', 'longitude', 'dttm', 'animal_id',)


class LastSightingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sighting
        fields = ('id', 'latitude', 'longitude', 'dttm',)


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ('id', 'vernacular_name',)


class AnimalSerializer(serializers.ModelSerializer):
    species = serializers.StringRelatedField()
    last_sighting = serializers.SerializerMethodField()
    species_id = serializers.PrimaryKeyRelatedField(queryset=Species.objects.all(), source='species')

    class Meta:
        model = Animal
        fields = ('id', 'name', 'species', 'species_id', 'last_sighting',)

    def get_last_sighting(self, container):
        last_sighting = Sighting.objects.filter(animal_id=container.id).order_by('-dttm').first()
        if last_sighting is not None:
            serializer = LastSightingSerializer(instance=last_sighting)
            return serializer.data
        return None

    def validate_name(self, value):
        if self.instance and self.instance.name == value:
            return value
        if Animal.objects.all().filter(name__iexact=value).first() is not None:
            raise serializers.ValidationError("Animal with this name already exists")
        return value

class AnimalReadOnlySerializer(serializers.ModelSerializer):
    species = serializers.StringRelatedField()

    class Meta:
        model = Animal
        fields = ('id', 'name', 'species',)

class SightingViewSerializer(serializers.ModelSerializer):
    animal = AnimalReadOnlySerializer()

    class Meta:
        model = Sighting
        fields = ('id', 'dttm', 'latitude', 'longitude', 'animal',)

class SightingSerializer(serializers.ModelSerializer):
    animal_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Sighting
        fields = ('id', 'dttm', 'latitude', 'longitude', 'animal_id',)