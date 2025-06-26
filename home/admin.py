from django.contrib import admin
# User management is now handled in the accounts app.
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_dummy')
    list_filter = ('is_dummy', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
