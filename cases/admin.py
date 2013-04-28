from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User

from models import Case, Event
from .forms import CaseForm
from .forms import CustomUserCreationForm


class EventInline(admin.TabularInline):
    model = Event
    extra = 2


class CaseAdmin(admin.ModelAdmin):
    model = Case
    list_display = ('signature', 'prosecutor_names', 'defendant_names', 'dispute_amount', 'date_added', )
    inlines = (EventInline,)
    form = CaseForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'status')}
        ),
    )
    list_display = ('last_name', 'first_name', 'email',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Case, CaseAdmin)
