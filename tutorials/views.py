from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Course, Lesson


def home(request):
    categories = Category.objects.all()
    featured_courses = Course.objects.filter(is_published=True).select_related("category")[:6]
    return render(
        request,
        "tutorials/home.html",
        {
            "categories": categories,
            "featured_courses": featured_courses,
        },
    )


def course_list(request, category_slug=None):
    courses = Course.objects.filter(is_published=True).select_related("category")

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        courses = courses.filter(category=category)

    level = request.GET.get("level")
    if level:
        courses = courses.filter(level=level)

    query = request.GET.get("q")
    if query:
        courses = courses.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(description__icontains=query)
        )

    return render(
        request,
        "tutorials/course_list.html",
        {
            "courses": courses,
            "categories": Category.objects.all(),
            "active_category": category,
            "active_level": level,
            "query": query or "",
        },
    )


def course_detail(request, course_slug):
    course = get_object_or_404(
        Course.objects.select_related("category"), slug=course_slug, is_published=True
    )
    lessons = course.lessons.all()
    return render(
        request,
        "tutorials/course_detail.html",
        {
            "course": course,
            "lessons": lessons,
        },
    )


def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    return render(
        request,
        "tutorials/lesson_detail.html",
        {
            "course": course,
            "lesson": lesson,
            "lessons": course.lessons.all(),
        },
    )


def about(request):
    return render(request, "tutorials/about.html")
