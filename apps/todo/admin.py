from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'important', 'is_completed')
    search_fields = ('title', 'author__username')
    readonly_fields = ('created_time', 'updated_time')
    list_filter = ('is_completed',)
