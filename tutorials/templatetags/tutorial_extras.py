from django import template

from tutorials.utils import get_embed_url

register = template.Library()


@register.filter
def embed_url(url):
    return get_embed_url(url)


@register.filter
def duration_display(minutes):
    minutes = minutes or 0
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"
