from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from movies.models import FilmWork
from movies.serializers import FilmWorkSerializer
from rest_framework import generics


@method_decorator(
    name="get",
    decorator=extend_schema(
        tags=["Киноленты"],
        description="Получить список кинолент",
    ),
)
class FilmWorkListView(generics.ListAPIView):
    queryset = FilmWork.objects.all()
    serializer_class = FilmWorkSerializer


@method_decorator(
    name="get",
    decorator=extend_schema(tags=["Киноленты"], description="Получить киноленту"),
)
class FilmWorkDetailView(generics.RetrieveAPIView):
    queryset = FilmWork.objects.all()
    serializer_class = FilmWorkSerializer
