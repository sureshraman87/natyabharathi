from django.core.management.base import BaseCommand

from tutorials.models import Category, Course, Lesson

DEMO_DATA = [
    {
        "category": "Foundations",
        "courses": [
            {
                "title": "Adavus for Absolute Beginners",
                "level": "beginner",
                "instructor": "Guru Smt. Kamala Devi",
                "summary": "The foundational basic steps (adavus) every Bharatanatyam student starts with.",
                "lessons": [
                    "Introduction to Thattadavu",
                    "Naattadavu, part 1",
                    "Naattadavu, part 2",
                    "Correct Aramandi (half-sit) posture",
                ],
            },
            {
                "title": "Hasta Mudras: The Language of Hands",
                "level": "beginner",
                "instructor": "Guru Smt. Kamala Devi",
                "summary": "Learn the 28 single-hand (asamyukta) gestures and how they're used in storytelling.",
                "lessons": [
                    "Pataka and Tripataka",
                    "Ardhachandra and Arala",
                    "Mayura and Ardhapataka",
                ],
            },
        ],
    },
    {
        "category": "Repertoire (Margam)",
        "courses": [
            {
                "title": "Alarippu: Your First Full Piece",
                "level": "intermediate",
                "instructor": "Guru Shri Ravi Shankar",
                "summary": "Step-by-step breakdown of Alarippu, the traditional opening dance of a margam.",
                "lessons": [
                    "Alarippu rhythm structure (jathi)",
                    "Neck and eye movements",
                    "Full Alarippu, slow tempo",
                    "Full Alarippu, performance tempo",
                ],
            },
            {
                "title": "Jatiswaram Essentials",
                "level": "intermediate",
                "instructor": "Guru Shri Ravi Shankar",
                "summary": "Pure dance (nritta) piece set to a raga, focusing on symmetry and rhythm.",
                "lessons": [
                    "Understanding the swara pattern",
                    "First charanam",
                    "Second charanam",
                ],
            },
        ],
    },
    {
        "category": "Abhinaya (Expression)",
        "courses": [
            {
                "title": "Introduction to Abhinaya",
                "level": "advanced",
                "instructor": "Guru Smt. Lakshmi Priya",
                "summary": "Facial expression and storytelling technique for padams and javalis.",
                "lessons": [
                    "The nine rasas explained",
                    "Eye movements (drishti bheda)",
                    "Interpreting a simple padam",
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Populate the database with sample categories, courses and lessons for local testing."

    def handle(self, *args, **options):
        created_courses = 0
        created_lessons = 0

        for cat_index, cat_data in enumerate(DEMO_DATA):
            category, _ = Category.objects.get_or_create(
                name=cat_data["category"],
                defaults={"slug": self._slugify(cat_data["category"]), "order": cat_index},
            )

            for course_index, course_data in enumerate(cat_data["courses"]):
                course, course_was_created = Course.objects.get_or_create(
                    title=course_data["title"],
                    defaults={
                        "slug": self._slugify(course_data["title"]),
                        "category": category,
                        "level": course_data["level"],
                        "instructor": course_data["instructor"],
                        "summary": course_data["summary"],
                        "description": course_data["summary"],
                        "order": course_index,
                    },
                )
                if course_was_created:
                    created_courses += 1

                for lesson_index, lesson_title in enumerate(course_data["lessons"]):
                    lesson, lesson_was_created = Lesson.objects.get_or_create(
                        course=course,
                        title=lesson_title,
                        defaults={
                            "slug": self._slugify(lesson_title),
                            "order": lesson_index,
                            "duration_minutes": 8 + lesson_index * 2,
                            "description": (
                                "Add your own video link in the Django admin "
                                "(Lesson -> video_url) to replace this placeholder."
                            ),
                            "is_free_preview": lesson_index == 0,
                        },
                    )
                    if lesson_was_created:
                        created_lessons += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_courses} course(s) and {created_lessons} lesson(s). "
                "Add real video URLs via /admin/."
            )
        )

    @staticmethod
    def _slugify(value):
        from django.utils.text import slugify

        return slugify(value)
