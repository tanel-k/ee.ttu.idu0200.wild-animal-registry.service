from django.db.models import Max, F
from rest_framework import generics

from .models import Animal, Sighting, Species
from .serializers import AnimalSerializer, SightingSerializer, SpeciesSerializer


class AnimalList(generics.ListCreateAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer


class AnimalDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer


class AnimalSightingsList(generics.ListAPIView):
    serializer_class = SightingSerializer

    def get_queryset(self):
        """
        This view returns a list of all the sightings
        for an animal.
        """
        animal_id = self.kwargs['animal_id']
        queryset = Sighting.objects.filter(animal_id=animal_id)

        latest_only = self.request.query_params.get('latest_only', False)
        print(bool(latest_only))
        if latest_only:
            queryset = queryset.latest('dttm')
        return queryset


class SightingList(generics.ListCreateAPIView):
    queryset = Sighting.objects.all()
    serializer_class = SightingSerializer


class SightingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sighting.objects.all()
    serializer_class = SightingSerializer


class SpeciesList(generics.ListAPIView):
    serializer_class = SpeciesSerializer

    def get_queryset(self):
        """
        This view returns a list of all the species
        optionally filtered by name.

        (see django.contrib.postgres.search)
        """
        queryset = Species.objects.all()
        vernacular_name = self.request.query_params.get('vernacular_name', None)
        if vernacular_name is not None:
            # use search index
            queryset = queryset.filter(vernacular_name__search=vernacular_name)
        return queryset

