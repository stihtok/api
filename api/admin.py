from django.contrib import admin

from .models import Stih, Author, Tags

class StihAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "createdAt"]

admin.site.register(Stih, StihAdmin)
admin.site.register(Author)
admin.site.register(Tags)

