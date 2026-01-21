from django.contrib import admin
from django.utils.html import format_html

from .models import Stih, Author, Tags


@admin.register(Stih)
class StihAdmin(admin.ModelAdmin):
    list_display = ["title_preview", "author", "tags_display", "body_preview", "likes", "createdAt"]
    list_filter = ["author", "tags", "createdAt", "likes"]
    search_fields = ["title", "body", "epigraph", "author__name"]
    list_editable = ["likes", "createdAt"]
    list_per_page = 25
    ordering = ["-likes", "title"]
    filter_horizontal = ["tags"]
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("title", "author", "tags", "createdAt")
        }),
        ("Текст стиха", {
            "fields": ("epigraph", "body"),
            "classes": ("wide",)
        }),
        ("Дополнительно", {
            "fields": ("likes",),
            "classes": ("collapse",)
        }),
    )
    
    actions = ["reset_likes", "duplicate_stih"]
    
    def title_preview(self, obj):
        """Короткое отображение названия"""
        if obj.title:
            return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
        return "(без названия)"
    title_preview.short_description = "Название"
    title_preview.admin_order_field = "title"
    
    def body_preview(self, obj):
        """Предпросмотр текста стиха"""
        if obj.body:
            preview = obj.body[:100].replace("\n", " ")
            return preview + "..." if len(obj.body) > 100 else preview
        return "-"
    body_preview.short_description = "Текст"
    
    def tags_display(self, obj):
        """Отображение тегов"""
        tags = obj.tags.all()
        if tags:
            return ", ".join([tag.title for tag in tags])
        return "-"
    tags_display.short_description = "Теги"
    
    def reset_likes(self, request, queryset):
        """Сбросить лайки у выбранных стихов"""
        count = queryset.update(likes=0)
        self.message_user(request, f"Лайки сброшены у {count} стих(ов).")
    reset_likes.short_description = "Сбросить лайки у выбранных стихов"
    
    def duplicate_stih(self, request, queryset):
        """Дублировать выбранные стихи"""
        count = 0
        for original_stih in queryset:
            # Сохраняем теги оригинала
            original_tags = list(original_stih.tags.all())
            # Создаем копию
            new_stih = Stih(
                author=original_stih.author,
                title=f"{original_stih.title} (копия)" if original_stih.title else "Копия",
                epigraph=original_stih.epigraph,
                body=original_stih.body,
                createdAt=original_stih.createdAt,
                likes=0
            )
            new_stih.save()
            # Восстанавливаем теги
            new_stih.tags.set(original_tags)
            count += 1
        self.message_user(request, f"Создано {count} копий стих(ов).")
    duplicate_stih.short_description = "Дублировать выбранные стихи"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "photo_preview", "stihs_count", "description_preview"]
    search_fields = ["name", "description"]
    list_per_page = 25
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "photo")
        }),
        ("Описание", {
            "fields": ("description",),
            "classes": ("wide",)
        }),
    )
    
    def photo_preview(self, obj):
        """Предпросмотр фотографии"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.photo.url
            )
        return "-"
    photo_preview.short_description = "Фото"
    
    def description_preview(self, obj):
        """Предпросмотр описания"""
        if obj.description:
            preview = obj.description[:100]
            return preview + "..." if len(obj.description) > 100 else preview
        return "-"
    description_preview.short_description = "Описание"
    
    def stihs_count(self, obj):
        """Количество стихов автора"""
        count = obj.stih_set.count()
        return format_html(
            '<a href="/admin/api/stih/?author__id__exact={}">{}</a>',
            obj.id, count
        )
    stihs_count.short_description = "Стихов"


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ["title", "stihs_count"]
    search_fields = ["title"]
    list_per_page = 25
    
    def stihs_count(self, obj):
        """Количество стихов с этим тегом"""
        count = obj.stih_set.count()
        return format_html(
            '<a href="/admin/api/stih/?tags__id__exact={}">{}</a>',
            obj.id, count
        )
    stihs_count.short_description = "Стихов"

