from django.contrib import admin

from .models import Stih, Author

class StihAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "createdAt"]

admin.site.register(Stih, StihAdmin)
admin.site.register(Author)

