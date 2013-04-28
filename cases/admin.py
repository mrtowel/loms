from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User

from models import Case, Event, CaseFile
from .forms import CaseForm
from .forms import CustomUserCreationForm
from .forms import CaseFileForm


class EventInline(admin.TabularInline):
    model = Event
    extra = 2


class CaseFileInline(admin.StackedInline):
    model = CaseFile
    extra = 1
    fields = ('file', 'date_added', 'user')
    readonly_fields = ('date_added', 'user')
    form = CaseFileForm

    def decrypt_date_added(self, obj):
        if obj.date_added:
            decrypt(obj.date_added)
        else:
            self.readonly_fields = ('date_added', 'file',)


class CaseAdmin(admin.ModelAdmin):
    model = Case
    list_display = ('signature', 'prosecutor_names', 'defendant_names', 'dispute_amount', 'date_added', )
    inlines = (EventInline, CaseFileInline,)
    form = CaseForm

    def save_model(self, request, obj, form, change):
        form = CaseFileForm
        self.user = request.user
        obj.save()


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
