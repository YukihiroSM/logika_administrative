from django.contrib import admin
from logika_general.models import Group, Location, Notification

admin.site.site_header = "Logika Administrative"
admin.site.site_title = "Logika Administrative"
admin.site.index_title = "Logika Administrative"
admin.site.register(Group)
admin.site.register(Location)
admin.site.register(Notification)
