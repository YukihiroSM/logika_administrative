from django.contrib import admin
from logika_general.models import Group, Location, Notification, ClientManagerProfile, TerritorialManagerProfile, RegionalManagerProfile

admin.site.site_header = "Logika Administrative"
admin.site.site_title = "Logika Administrative"
admin.site.index_title = "Logika Administrative"
admin.site.register(Group)
admin.site.register(Location)
admin.site.register(Notification)
admin.site.register(ClientManagerProfile)
admin.site.register(TerritorialManagerProfile)
admin.site.register(RegionalManagerProfile)
