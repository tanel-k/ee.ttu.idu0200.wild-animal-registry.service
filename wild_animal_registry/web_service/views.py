from itertools import groupby

from django.http import Http404
from django.db.models import Q
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework import status

from .models import Animal, Sighting, Species
from .serializers import AnimalSerializer, AnimalSightingSerializer, SpeciesSerializer, SightingSerializer


class AnimalList(generics.ListCreateAPIView):
    serializer_class = AnimalSerializer

    def get_queryset(self):
        """
        This view returns a list of all animals
        optionally filtered by name or name of species
        """
        queryset = Animal.objects.all()
        name_or_species = self.request.query_params.get('name_or_species', None)
        if name_or_species is not None:
            # __search suffix triggers search index
            # (see django.contrib.postgres.search)
            queryset = queryset.filter(
                Q(species__vernacular_name__search=name_or_species) | Q(name__search=name_or_species))
        return queryset


class AnimalDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer


class AnimalSightingsView(views.APIView):
    """
    Shared methods for animal sightings views
    """
    def get_animal(self, pk):
        try:
            return Animal.objects.get(pk=pk)
        except Animal.DoesNotExist:
            raise Http404

    def get_sighting(self, pk, animal_id):
        try:
            return Sighting.objects.filter(animal_id=animal_id).get(pk=pk)
        except Sighting.DoesNotExist:
            raise Http404


class AnimalSightingsList(AnimalSightingsView):
    """
    View of all the sightings of an animal.
    """
    def get(self, request, animal_id):
        sightings = Sighting.objects.filter(animal_id=animal_id).order_by('-dttm')
        serializer = AnimalSightingSerializer(sightings, many=True)
        return Response(serializer.data)

    def post(self, request, animal_id):
        animal = self.get_animal(animal_id)
        request.data['animal_id'] = animal.pk
        serializer = AnimalSightingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnimalSightingDetail(AnimalSightingsView):
    """
    View of a specific sighting of an animal.
    """
    def get(self, request, animal_id, pk):
        sighting = self.get_sighting(pk, animal_id)
        serializer = AnimalSightingSerializer(sighting)
        return Response(serializer.data)

    def put(self, request, animal_id, pk):
        sighting = self.get_sighting(pk, animal_id)
        serializer = AnimalSightingSerializer(sighting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, animal_id, pk):
        sighting = self.get_sighting(animal_id, pk)
        sighting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SpeciesList(generics.ListAPIView):
    serializer_class = SpeciesSerializer

    def get_queryset(self):
        """
        This view returns a list of all species
        optionally filtered by name.
        """
        queryset = Species.objects.all()
        vernacular_name = self.request.query_params.get('vernacular_name', None)
        if vernacular_name is not None:
            # __search suffix triggers search index
            queryset = queryset.filter(vernacular_name__search=vernacular_name)
        return queryset


class SightingsList(views.APIView):
    def get(self, request):
        """
        This view returns the latest sightings of animals.
        If an animal has been seen in the same location more than once,
        only the latest sighting is returned in the result set.
        """
        sightings = Sighting.objects.all().order_by('latitude', 'longitude')
        # group by latitude and longitude
        sightings_grouped = {lat_lng: list(sightings) for lat_lng, sightings
                             in groupby(sightings, lambda sighting: (sighting.latitude, sighting.longitude))}

        # nested group for animal_id
        for lat_lng in sightings_grouped:
            lat_lng_sightings = sorted(sightings_grouped[lat_lng], key=lambda sighting: sighting.animal_id)
            # groupby only groups contiguous elements
            sightings_grouped[lat_lng] = {animal_id: list(sightings) for animal_id, sightings
                                          in groupby(lat_lng_sightings, lambda sighting: sighting.animal_id)}

        # for each sighting of an animal in the same location get the latest sighting
        filtered_sightings = []
        for lat_lng in sightings_grouped:
            lat_lng_sightings = sightings_grouped[lat_lng]
            for animal_id in lat_lng_sightings:
                animal_sightings = \
                    sorted(lat_lng_sightings[animal_id], key=lambda sighting: sighting.dttm, reverse=True)
                filtered_sightings.append(animal_sightings[0])

        serializer = SightingSerializer(filtered_sightings, many=True)
        return Response(serializer.data)
