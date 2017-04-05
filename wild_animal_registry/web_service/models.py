from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError


class Animal(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    species = models.ForeignKey('Species', models.DO_NOTHING)

    class Meta:
        db_table = 'animal'

    def __str__(self):
        return self.name


class Sighting(models.Model):
    id = models.BigAutoField(primary_key=True)
    dttm = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    animal = models.ForeignKey(Animal, models.CASCADE)

    class Meta:
        db_table = 'sighting'

    def clean(self):
        if not is_latitude_valid(self.latitude):
            raise ValidationError('Invalid latitude')

        if not is_longitude_valid(self.longitude):
            raise ValidationError('Invalid longitude')

    def __str__(self):
        return 'lat=' + str(self.latitude) + ' lng=' + str(self.longitude)


class Species(models.Model):
    id = models.BigAutoField(primary_key=True)
    vernacular_name = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = False
        db_table = 'species'

    def __str__(self):
        return self.vernacular_name


def is_latitude_valid(latitude):
    return -90.0 <= latitude <= 90.0


def is_longitude_valid(longitude):
    return -180.0 <= longitude <= 180.0
