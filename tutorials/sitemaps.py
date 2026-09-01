from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Lesson


class LessonSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Lesson.objects.filter(course__is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["home", "course_list", "about"]

    def location(self, item):
        return reverse(item)
