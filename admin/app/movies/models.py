from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from movies.model_mixins import CreatedMixin, CreatedModifiedMixin, UUIDMixin


class Genre(UUIDMixin, CreatedModifiedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = "content\".\"genre"  # fmt: skip
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class FilmWork(UUIDMixin, CreatedModifiedMixin):
    class Type(models.TextChoices):
        MOVIE = "movie", _("movie")
        TV_SHOW = "tv_show", _("tv_show")

    title = models.CharField(_("title"), max_length=255, db_index=True)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation_date"), null=True, blank=True)
    file_path = models.FileField(_("file_path"), null=True, blank=True)
    rating = models.FloatField(
        _("rating"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_("type"), choices=Type.choices, db_index=True)

    genres = models.ManyToManyField(
        "Genre", through="GenreFilmwork", related_name="film_works"
    )
    persons = models.ManyToManyField(
        "Person", through="PersonFilmwork", related_name="film_works"
    )

    class Meta:
        db_table = "content\".\"film_work"  # fmt: skip
        verbose_name = _("FilmWork")
        verbose_name_plural = _("FilmWorks")

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin, CreatedMixin):
    film_work = models.ForeignKey(
        "FilmWork", on_delete=models.CASCADE, verbose_name=_("film_work")
    )
    genre = models.ForeignKey(
        "Genre", on_delete=models.CASCADE, verbose_name=_("genre")
    )

    class Meta:
        db_table = "content\".\"genre_film_work"  # fmt: skip
        verbose_name = _("Filmwork genre")
        verbose_name_plural = _("Filmworks genres")
        unique_together = [["film_work", "genre"]]

    def __str__(self):
        return f"{self.film_work} - {self.genre}"


class Person(UUIDMixin, CreatedModifiedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        db_table = "content\".\"person"  # fmt: skip
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin, CreatedMixin):
    class Role(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    film_work = models.ForeignKey(
        "FilmWork", on_delete=models.CASCADE, verbose_name=_("film_work")
    )
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, verbose_name=_("person")
    )
    role = models.CharField(_("role"), choices=Role.choices, max_length=255)

    class Meta:
        db_table = "content\".\"person_film_work"  # fmt: skip
        verbose_name = _("Filmwork person")
        verbose_name_plural = _("Filmworks persons")
        unique_together = [["person", "film_work", "role"]]
        index_together = [["person", "role"]]

    def __str__(self):
        return f"{self.film_work} - {self.person} - {self.role}"
