def get_conversion(payments, attended):
    if payments == 0 and attended == 0:
        conversion = 0
    else:
        try:
            conversion = round((payments / attended) * 100, 2)
        except ZeroDivisionError:
            conversion = 100
    return conversion if conversion else 0
