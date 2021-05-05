from django import template

register = template.Library()


@register.filter(is_safe=False)
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(is_safe=False)
def get_attr(obj, attr):
    return getattr(obj, attr, None)


@register.filter(is_safe=False)
def div_get_mod(number, limit):
    d = divmod(number, limit)
    return d[1] == 0
