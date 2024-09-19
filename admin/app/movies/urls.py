from django.urls import path
from movies.views import FilmWorkDetailView, FilmWorkListView

urlpatterns = [
    path("", FilmWorkListView.as_view(), name="movies"),
    path("<uuid:pk>", FilmWorkDetailView.as_view(), name="movie"),
]
