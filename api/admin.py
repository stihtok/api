import json
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from .models import Stih, Author, Tags


@admin.register(Stih)
class StihAdmin(admin.ModelAdmin):
    list_display = ["id", "title_preview", "author", "tags_display", "body_preview", "likes", "createdAt"]
    list_filter = ["author", "tags", "createdAt", "likes"]
    search_fields = ["title", "body", "epigraph", "author__name"]
    list_editable = ["likes", "createdAt"]
    list_per_page = 25
    ordering = ["-id"]
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
    
    actions = ["reset_likes", "duplicate_stih", "export_to_json"]
    
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
    
    def export_to_json(self, request, queryset):
        """Экспортировать выбранные стихи в JSON файл"""
        stihs_data = []
        for stih in queryset:
            # Получаем ID всех тегов стиха
            tag_ids = [tag.id for tag in stih.tags.all()]
            stih_data = {
                "author_id": stih.author.id,
                "tag_ids": tag_ids,
                "title": stih.title or "",
                "body": stih.body or "",
                "epigraph": stih.epigraph or "",
                "createdAt": stih.createdAt or "",
                "likes": stih.likes,
            }
            stihs_data.append(stih_data)
        
        # Создаем JSON ответ
        json_data = json.dumps(stihs_data, ensure_ascii=False, indent=2)
        response = HttpResponse(json_data, content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="stihs_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    export_to_json.short_description = "Экспортировать выбранные стихи в JSON"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_json_url'] = 'admin:api_stih_import_json'
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-json/', self.admin_site.admin_view(self.import_json_view), name='api_stih_import_json'),
        ]
        return custom_urls + urls
    
    def import_json_view(self, request):
        """View для импорта стихов из JSON файла"""
        if request.method == 'POST':
            json_file = request.FILES.get('json_file')
            default_author_id = request.POST.get('author_id')
            
            if not json_file:
                messages.error(request, "Пожалуйста, выберите файл для загрузки.")
                return redirect('admin:api_stih_import_json')
            
            # Получаем автора по умолчанию, если указан
            default_author = None
            if default_author_id:
                try:
                    default_author = Author.objects.get(id=default_author_id)
                except Author.DoesNotExist:
                    messages.error(request, f"Автор с ID {default_author_id} не найден.")
                    return redirect('admin:api_stih_import_json')
            
            try:
                # Читаем и парсим JSON
                file_content = json_file.read().decode('utf-8')
                data = json.loads(file_content)
                
                if not isinstance(data, list):
                    messages.error(request, "JSON должен содержать массив объектов.")
                    return redirect('admin:api_stih_import_json')
                
                # Проверяем, есть ли хотя бы один author_id в данных
                has_author_ids = any(item.get('author_id') for item in data if isinstance(item, dict))
                
                # Если в JSON нет author_id и не выбран автор по умолчанию, выдаем ошибку
                if not has_author_ids and not default_author:
                    messages.error(request, "В JSON нет author_id и не выбран автор по умолчанию. Пожалуйста, выберите автора или убедитесь, что в JSON есть поле author_id.")
                    return redirect('admin:api_stih_import_json')
                
                imported_count = 0
                skipped_count = 0
                author_not_found_count = 0
                tags_not_found_count = 0
                
                for item in data:
                    # Проверяем наличие обязательных полей
                    if not all(key in item for key in ['title', 'body']):
                        skipped_count += 1
                        continue
                    
                    # Определяем автора: сначала из JSON, потом из формы
                    author_id = item.get('author_id')
                    if author_id:
                        try:
                            author = Author.objects.get(id=author_id)
                        except Author.DoesNotExist:
                            # Если автор из JSON не найден, используем автора по умолчанию
                            if default_author:
                                author = default_author
                            else:
                                author_not_found_count += 1
                                skipped_count += 1
                                continue
                    else:
                        # Если в JSON нет author_id, используем автора из формы
                        # Эта проверка уже выполнена выше, но оставляем для безопасности
                        if default_author:
                            author = default_author
                        else:
                            skipped_count += 1
                            continue
                    
                    # Обрабатываем title: убираем знаки препинания в конце
                    title = item.get('title', '').rstrip('.,;:!?…—–-')
                    
                    # Обрабатываем createdAt
                    createdAt_raw = item.get('createdAt')
                    if createdAt_raw is None:
                        createdAt = ''
                    else:
                        createdAt = str(createdAt_raw).replace('<', '').replace('>', '')
                    
                    # Обрабатываем теги
                    tag_ids = item.get('tag_ids', [])
                    tags_to_add = []
                    if tag_ids and isinstance(tag_ids, list):
                        for tag_id in tag_ids:
                            try:
                                tag = Tags.objects.get(id=tag_id)
                                tags_to_add.append(tag)
                            except Tags.DoesNotExist:
                                tags_not_found_count += 1
                                # Продолжаем импорт, просто пропускаем этот тег
                            except (ValueError, TypeError):
                                # Пропускаем невалидные ID
                                tags_not_found_count += 1
                    
                    # Создаем стих
                    try:
                        stih = Stih.objects.create(
                            author=author,
                            title=title,
                            body=item.get('body', ''),
                            createdAt=createdAt,
                            epigraph=item.get('epigraph', ''),
                            likes=item.get('likes', 0)
                        )
                        # Добавляем теги
                        if tags_to_add:
                            stih.tags.set(tags_to_add)
                        imported_count += 1
                    except Exception as e:
                        skipped_count += 1
                        continue
                
                message_parts = [f"Импортировано: {imported_count}"]
                if skipped_count > 0:
                    message_parts.append(f"Пропущено: {skipped_count}")
                if author_not_found_count > 0:
                    message_parts.append(f"Автор не найден: {author_not_found_count}")
                if tags_not_found_count > 0:
                    message_parts.append(f"Тегов не найдено: {tags_not_found_count}")
                
                messages.success(
                    request,
                    f"Импорт завершен. {'; '.join(message_parts)}."
                )
                return redirect('admin:api_stih_changelist')
                
            except json.JSONDecodeError:
                messages.error(request, "Ошибка: файл не является валидным JSON.")
                return redirect('admin:api_stih_import_json')
            except Exception as e:
                messages.error(request, f"Ошибка при импорте: {str(e)}")
                return redirect('admin:api_stih_import_json')
        
        # GET запрос - показываем форму
        authors = Author.objects.all().order_by('name')
        context = {
            'authors': authors,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/api/stih/import_json.html', context)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "photo_preview", "stihs_count", "description_preview"]
    search_fields = ["name", "description"]
    list_per_page = 25
    ordering = ["-id"]
    
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

