from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def format_large_number(value):
    """Format large numbers with K, M suffix"""
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return "0"
