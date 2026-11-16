
from django.contrib import admin
from django.utils import timezone

from .models import Category, Comment, ServiceRequest, WorkOrder


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "body", "is_internal", "created_at")
    readonly_fields = ("created_at",)


class OverdueFilter(admin.SimpleListFilter):
    title = "due date"
    parameter_name = "overdue"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Overdue"),
            ("no", "Not overdue"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                due_at__lt=timezone.now(),
                due_at__isnull=False,
            )

        if self.value() == "no":
            return queryset.filter(
                due_at__gte=timezone.now()
            ) | queryset.filter(due_at__isnull=True)

        return queryset


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "requester",
        "priority",
        "status",
        "due_at",
        "resolution_summary",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "category",
        OverdueFilter,
    )

    search_fields = (
        "title",
        "description",
        "location",
        "resolution_summary",
        "requester__username",
    )

    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("requester", "category")
    date_hierarchy = "created_at"
    inlines = (CommentInline,)


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "technician",
        "started_at",
        "completed_at",
    )

    search_fields = (
        "service_request__title",
        "technician__username",
    )

    autocomplete_fields = ("service_request", "technician")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "author",
        "is_internal",
        "created_at",
    )

    list_filter = ("is_internal", "created_at")

    search_fields = (
        "body",
        "service_request__title",
        "author__username",
    )
