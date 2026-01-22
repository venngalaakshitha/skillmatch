from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
        "uploaded_at",
        "has_text"
    )
    readonly_fields = ("extracted_text",)

    def has_text(self, obj):
        return bool(obj.extracted_text)

    has_text.boolean = True
    has_text.short_description = "Text Extracted"


