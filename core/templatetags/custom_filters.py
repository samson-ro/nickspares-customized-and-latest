
from django import template

register = template.Library()

@register.filter
def zip_lists(a, b):
    try:
        return zip(a, b)
    except:
        return []
