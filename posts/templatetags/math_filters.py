from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply two numbers safely."""
    try:
        return int(value) * int(arg)
    except:
        return 0


@register.filter
def cap100(value):
    """Prevent value from exceeding 100 (for chart bar widths)."""
    try:
        value = int(value)
        return 100 if value > 100 else value
    except:
        return 0
