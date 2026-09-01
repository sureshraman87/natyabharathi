from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("courses/", views.course_list, name="course_list"),
    path("category/<slug:category_slug>/", views.course_list, name="category_detail"),
    path("courses/<slug:course_slug>/", views.course_detail, name="course_detail"),
    path(
        "courses/<slug:course_slug>/<slug:lesson_slug>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
]
