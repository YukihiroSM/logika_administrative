from django import template

register = template.Library()


@register.simple_tag
def calculate_conversion(payments_amount, attended_students):
    if payments_amount == 0 and attended_students == 0:
        conversion = 0
    else:
        try:
            conversion = (payments_amount / attended_students * 100, 2)
        except ZeroDivisionError:
            conversion = 100
    return f"{conversion:.2f}%"
