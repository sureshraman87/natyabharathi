from django.contrib import admin

from .models import Category, Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("order", "title", "slug", "video_url", "video_file", "duration_minutes", "is_free_preview")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "instructor", "is_published", "lesson_count", "order")
    list_filter = ("category", "level", "is_published")
    search_fields = ("title", "instructor", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "duration_minutes", "is_free_preview")
    list_filter = ("course__category", "is_free_preview")
    search_fields = ("title", "course__title")
    prepopulated_fields = {"slug": ("title",)}
