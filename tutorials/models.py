from django.db import models
from django.urls import reverse

LEVEL_CHOICES = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]


class Category(models.Model):
    """A grouping of courses, e.g. Adavus, Hastas, Padams, Theory."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", args=[self.slug])


class Course(models.Model):
    """A structured series of lessons, e.g. 'Alarippu for Beginners'."""

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    instructor = models.CharField(max_length=120, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.slug])

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def total_duration_minutes(self):
        return sum((lesson.duration_minutes or 0) for lesson in self.lessons.all())


class Lesson(models.Model):
    """A single video lesson within a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(
        blank=True,
        help_text="YouTube or Vimeo link, e.g. https://www.youtube.com/watch?v=XXXX",
    )
    video_file = models.FileField(
        upload_to="lesson_videos/",
        blank=True,
        null=True,
        help_text="Optional self-hosted video file, used if no video URL is set.",
    )
    duration_minutes = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_free_preview = models.BooleanField(
        default=True, help_text="Free previews are visible without restriction."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "order", "id"]
        unique_together = [("course", "slug")]

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    def get_absolute_url(self):
        return reverse("lesson_detail", args=[self.course.slug, self.slug])

    @property
    def next_lesson(self):
        return (
            Lesson.objects.filter(course=self.course, order__gt=self.order)
            .order_by("order", "id")
            .first()
        )

    @property
    def previous_lesson(self):
        return (
            Lesson.objects.filter(course=self.course, order__lt=self.order)
            .order_by("-order", "-id")
            .first()
        )
