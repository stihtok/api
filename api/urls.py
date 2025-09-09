from django.urls import path
from . import views

urlpatterns = [
    path("", views.getRoutes, name="routes"),
    path("stih/", views.getStih, name="Stih"),
    path("stih/<int:id>", views.getStihById, name="StihById"),
    path("stih/<int:id>/like", views.stihLike, name="StihLike"),
    path("stih/<int:id>/dislike", views.stihDislike, name="StihDislike"),
    path("bundle/", views.getStihBundle, name="StihBundle"),
    path("author/<int:id>", views.getAuthorById, name="AuthorById"),
    path("author/<int:id>/all", views.getAllStihByAuthorId, name="AllStihByAuthorId"),
    path("author/<int:id>/all/random", views.getAllStihByAuthorIdRandom, name="AllStihByAuthorIdRandom"),
    path("year/<int:year>/all", views.getAllStihByYear, name="AllStihByYear"),
    path("authors/", views.getAuthors, name="Authors"),
    path("tags/", views.getTags, name="Tags"),
    path("tags/<int:id>", views.getStihsByTag, name="Stihs by tag"),
    path("tags/query", views.getStihsByQuery, name="Stihs by query"),
    path("search/<str:searchString>", views.search, name="Search"),
]