from django.contrib import admin
from .models import User, Event

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "name", "email", "role", "status", "created_at")
    search_fields = ("name", "email")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "location", "status", "capacity")
    list_filter = ("status", "date")
    search_fields = ("title", "location")
    filter_horizontal = ("attendees",)
