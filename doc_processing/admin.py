from django.contrib import admin
from django.utils import timezone
from .models import Document

class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'processed_at']
    search_fields = ['title']
    readonly_fields = ['processed_at']
    
    def get_queryset(self, request):
        """Only show processed documents (processed_at is not null)"""
        qs = super().get_queryset(request)
        return qs.filter(processed_at__isnull=False)
    
    def has_add_permission(self, request):
        """Disable adding documents through processed view"""
        return False
    
    actions = ['unprocess_documents']
    
    def unprocess_documents(self, request, queryset):
        """Process selected documents"""
        updated = queryset.update(processed_at=None)
        self.message_user(request, f'{updated} documents processed successfully.')
    unprocess_documents.short_description = "Unprocess selected documents"

class UnprocessedDocumentAdmin(admin.ModelAdmin):
    exclude = ('title', 'processed_at',) 
    list_display = ['title']
    search_fields = ['title']
    
    def get_queryset(self, request):
        """Only show unprocessed documents (processed_at is null)"""
        qs = super().get_queryset(request)
        return qs.filter(processed_at__isnull=True)
    
    # Actions for unprocessed documents
    actions = ['process_documents']
    
    def process_documents(self, request, queryset):
        """Process selected documents"""
        updated = queryset.update(processed_at=timezone.now())
        self.message_user(request, f'{updated} documents processed successfully.')
    process_documents.short_description = "Process selected documents"


# Create proxy models for cleaner admin interface
class ProcessedDocumentProxy(Document):
    class Meta:
        proxy = True
        verbose_name = "Processed Document"
        verbose_name_plural = "Processed Documents"


class UnprocessedDocumentProxy(Document):
    class Meta:
        proxy = True
        verbose_name = "Unprocessed Document" 
        verbose_name_plural = "Unprocessed Documents"


# Register the admin classes
admin.site.register(ProcessedDocumentProxy, ProcessedDocumentAdmin)
admin.site.register(UnprocessedDocumentProxy, UnprocessedDocumentAdmin)
