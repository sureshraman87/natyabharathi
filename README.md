# Natya Bharathi

A Django-based video tutorial site for teaching **Bharatanatyam**, the
classical Indian dance form. Content is organised into **Categories** →
**Courses** → **Lessons**, where each lesson is a single video (YouTube,
Vimeo, or a self-hosted file) with a title, description and duration.

Built to be deployed at **https://natyabharathi.sureshraman.com** — see
[`DEPLOYMENT.md`](DEPLOYMENT.md) for step-by-step production setup.

## Features

- **Course catalogue** — courses grouped by category (Foundations,
  Repertoire, Abhinaya, ...) with level tags (Beginner/Intermediate/Advanced),
  search, and category/level filtering.
- **Lesson player** — embeds YouTube/Vimeo links automatically (paste a
  normal `youtube.com/watch?v=...` or `vimeo.com/...` URL — no manual embed
  code needed), or serves a self-hosted video file. Includes previous/next
  lesson navigation.
- **Content management via Django admin** — no code changes needed to add
  courses or lessons; instructors log in at `/admin/`.
- **SEO basics** — per-page titles/descriptions and an auto-generated
  `/sitemap.xml`.
- **Production-ready out of the box** — WhiteNoise for static files,
  environment-variable configuration (`django-environ`), HTTPS/HSTS
  hardening, and ready-to-use Gunicorn + Nginx + systemd config in `deploy/`.

## Content model

| Model    | Purpose                                                        |
|----------|-----------------------------------------------------------------|
| Category | A broad topic, e.g. "Foundations", "Repertoire (Margam)".        |
| Course   | A themed series of lessons, e.g. "Alarippu: Your First Piece".   |
| Lesson   | One video: title, video URL or file, description, duration.     |

## Local development

### Prerequisites

- Python 3.11+
- pip / venv

### Setup

```bash
git clone <this-repo-url>
cd natyabharathi

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env if you want, defaults work for local dev (SQLite, DEBUG=True).

python manage.py migrate
python manage.py createsuperuser

# Optional: populate a handful of sample courses/lessons to explore the UI.
python manage.py seed_demo_content

python manage.py runserver
```

Visit:

- http://127.0.0.1:8000/ — the public site
- http://127.0.0.1:8000/admin/ — content management

### Adding a course and lesson

1. Go to `/admin/`, log in with your superuser account.
2. Create a **Category** (e.g. "Foundations") if one doesn't already fit.
3. Create a **Course**: give it a title (the slug auto-fills), pick a
   category and level, and write a short summary.
4. Scroll down to the inline **Lessons** section on the same course page (or
   go to Lessons → Add) and add each video lesson:
   - **video_url**: paste a normal YouTube or Vimeo link, e.g.
     `https://www.youtube.com/watch?v=XXXXXXXXXXX`. It's converted to an
     embeddable player automatically — no embed code needed.
   - Alternatively use **video_file** to upload a video directly (stored
     under `media/lesson_videos/`), if you're not hosting on YouTube/Vimeo.
   - Set `order` to control playback/listing order within the course.
5. Save. The course/lesson immediately appear on the public site (as long as
   the course's `is_published` checkbox is on).

### Running tests / checks

```bash
python manage.py check
python manage.py test
```

## Project layout

```
natyabharathi_site/   Django project settings, URLs, WSGI/ASGI entrypoints
tutorials/             The app: models, views, admin, templates, sitemaps
templates/base.html    Site-wide layout (header/nav/footer)
static/css/style.css   All styling (no build step, no JS framework)
deploy/                Gunicorn systemd unit + Nginx config + deploy script
```

## Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full instructions on deploying this
project to a server so it's reachable at
**https://natyabharathi.sureshraman.com**.
