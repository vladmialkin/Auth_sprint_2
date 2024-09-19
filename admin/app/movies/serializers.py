from django.db.models import Prefetch
from movies.models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmwork
from rest_framework import serializers


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "description")


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("full_name",)


class FilmWorkSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField("get_genres")
    actors = serializers.SerializerMethodField("get_actors")
    writers = serializers.SerializerMethodField("get_writers")
    directors = serializers.SerializerMethodField("get_directors")

    def get_genres(self, obj):
        return Prefetch(
            "genrefilmwork_set",
            queryset=GenreFilmwork.objects.filter(film_work=obj),
            to_attr="all_genres",
        )

    def get_actors(self, obj):
        return Prefetch(
            "personfilmwork_set",
            queryset=PersonFilmwork.objects.filter(role=PersonFilmwork.Role.ACTOR),
            to_attr="actors",
        )

    def get_writers(self, obj):
        return Prefetch(
            "personfilmwork_set",
            queryset=PersonFilmwork.objects.filter(role=PersonFilmwork.Role.WRITER),
            to_attr="writers",
        )

    def get_directors(self, obj):
        return Prefetch(
            "personfilmwork_set",
            queryset=PersonFilmwork.objects.filter(role=PersonFilmwork.Role.DIRECTOR),
            to_attr="directors",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        instance = FilmWork.objects.prefetch_related(
            representation["genres"],
            representation["actors"],
            representation["writers"],
            representation["directors"],
        ).get(pk=instance.pk)

        representation["genres"] = [
            genrefilmwork.genre.name for genrefilmwork in instance.all_genres
        ]
        representation["actors"] = [
            personfilnwork.person.full_name for personfilnwork in instance.actors
        ]
        representation["writers"] = [
            personfilnwork.person.full_name for personfilnwork in instance.writers
        ]
        representation["directors"] = [
            personfilnwork.person.full_name for personfilnwork in instance.directors
        ]

        return representation

    class Meta:
        model = FilmWork
        fields = (
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "genres",
            "actors",
            "writers",
            "directors",
        )
