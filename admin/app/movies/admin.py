from django.contrib import admin
from movies.models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ("genre",)


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ("person",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "id",
        "name",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)

    search_fields = (
        "id",
        "full_name",
    )


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = (
        "title",
        "description",
        "type",
        "creation_date",
        "rating",
    )

    list_filter = (
        "type",
        "creation_date",
        "rating",
    )

    search_fields = (
        "id",
        "title",
    )
