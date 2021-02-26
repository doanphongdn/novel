from django import template

register = template.Library()


@register.filter(is_safe=False)
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(is_safe=False)
def get_attr(obj, attr):
    return getattr(obj, attr, None)


@register.tag(name="current_time")
def do_current_time(parser, token):
    return "aaaaaaaaaaaaaaaa"
