from django.contrib import admin
from .models import User,CreateNotes,Labels,MapLabel
# from adminplus.sites import AdminSitePlus

admin.site.register(User)
admin.site.register(CreateNotes)
admin.site.register(Labels)
admin.site.register(MapLabel)

admin.autodiscover()