from django.contrib import admin

from backend.models import Publication, Comment, Like, Photo

# Register your models here.
admin.site.register(Publication)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Photo)