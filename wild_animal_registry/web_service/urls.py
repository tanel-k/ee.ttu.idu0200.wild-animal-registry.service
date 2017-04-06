from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^animals/(?P<animal_id>[0-9]+)/sightings$', views.AnimalSightingsList.as_view()),
    url(r'^animals/(?P<animal_id>[0-9]+)/sightings/(?P<pk>[0-9]+)$', views.AnimalSightingDetail.as_view()),

    url(r'^animals/(?P<pk>[0-9]+)$', views.AnimalDetail.as_view()),
    url(r'^animals', views.AnimalList.as_view()),

    url(r'^species', views.SpeciesList.as_view()),

    url(r'^sightings', views.SightingsList.as_view()),
];
