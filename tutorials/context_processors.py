from django.conf import settings


def site_metadata(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
    }
