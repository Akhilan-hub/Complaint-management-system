from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'ai_verification_status', 'created_at', 'resolved_at')
    list_filter = ('status', 'ai_verification_status', 'resolution_ai_status')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
