from django import template

register = template.Library()

@register.filter
def status(item):
    if item.enabled == True or item.enabled == 'true':
        return 'enabled'
    else:
        return 'disabled'