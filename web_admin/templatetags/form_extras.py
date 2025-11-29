from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """Return field rendered with the given CSS class added to its widget.

    Usage in template: {{ field|add_class:"form-control" }}
    """
    try:
        return field.as_widget(attrs={"class": css_class})
    except Exception:
        return field


@register.filter(name='add_attr')
def add_attr(field, attr):
    """Add arbitrary attribute in the form 'name:value' to a field widget.

    Usage: {{ field|add_attr:"placeholder:Escribe..." }}
    """
    try:
        name, val = attr.split(':', 1)
        return field.as_widget(attrs={name: val})
    except Exception:
        return field
